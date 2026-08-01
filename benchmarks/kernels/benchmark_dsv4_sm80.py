# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: Copyright contributors to the vLLM project
"""Microbenchmarks for the DeepSeek-V4-Flash SM8x kernels.

Shapes default to DSv4-Flash-0731 at TP=8 (8 local heads, head_dim 512,
hidden 4096, hc_mult 4), the configuration whose profile motivated the tuning
knobs each sweep exposes. Sweeps launch the kernels directly so the tuning
parameters (split count, head block, worker count) are explicit rather than
whatever the production heuristic picks.

Examples:
    python benchmarks/kernels/benchmark_dsv4_sm80.py --kernel sparse-decode
    python benchmarks/kernels/benchmark_dsv4_sm80.py --kernel all
"""

import argparse
import itertools
from collections.abc import Callable
from functools import partial

import torch

from vllm.triton_utils import triton

# Every value below that also exists in the checkpoint is named after its
# config.json key, because guessing one has already produced a wrong conclusion
# here: a placeholder sinkhorn count of 3 against the real 20 changed the mHC pre
# per-launch cost from 5.2 to 8.3 us *and* changed which component dominated.
# DeepSeek-V4-Flash-0731 config.json, verified 2026-08-01.
CFG_HEAD_DIM = 512  # head_dim
CFG_QK_ROPE_HEAD_DIM = 64  # qk_rope_head_dim
CFG_HIDDEN_SIZE = 4096  # hidden_size
CFG_NUM_ATTENTION_HEADS = 64  # num_attention_heads
CFG_NUM_HIDDEN_LAYERS = 43  # num_hidden_layers
CFG_HC_MULT = 4  # hc_mult
CFG_HC_SINKHORN_ITERS = 20  # hc_sinkhorn_iters
CFG_SLIDING_WINDOW = 128  # sliding_window
CFG_INDEX_TOPK = 512  # index_topk

TP_SIZE = 8

# MLA head geometry. The nope width is the remainder, not an independent number.
HEAD_DIM = CFG_HEAD_DIM
ROPE_DIM = CFG_QK_ROPE_HEAD_DIM
NOPE_DIM = HEAD_DIM - ROPE_DIM  # 448
SCALE = HEAD_DIM**-0.5

# fp8_ds_mla cache entry: nope as fp8, rope as bf16, one ue8m0 scale per
# quantization block (7 real + 1 pad).
QUANT_BLOCK = 64
SCALE_DIM = 8
CACHE_TOKEN_BYTES = NOPE_DIM + ROPE_DIM * 2  # 576
CACHE_ENTRY_BYTES = CACHE_TOKEN_BYTES + SCALE_DIM  # 584
CACHE_BLOCK_SIZE = 64  # vLLM paged block size, not a checkpoint value

NUM_HEADS = CFG_NUM_ATTENTION_HEADS // TP_SIZE  # 8 local heads
HIDDEN_SIZE = CFG_HIDDEN_SIZE
HC_MULT = CFG_HC_MULT
HC_MULT3 = HC_MULT * (2 + HC_MULT)  # 24 prenorm GEMM outputs
SINKHORN_ITERS = CFG_HC_SINKHORN_ITERS

# Decode walks sliding_window SWA tokens plus index_topk compressed tokens per
# query, independent of context length.
SWA_LEN = CFG_SLIDING_WINDOW
TOPK_LEN = CFG_INDEX_TOPK

# mHC pre runs twice per layer (attention and FFN) plus one broadcast variant for
# the first layer, which is what per-step totals below are scaled by.
MHC_PRE_LAUNCHES_PER_STEP = 2 * CFG_NUM_HIDDEN_LAYERS + 1  # 87


def _time_us(fn: Callable[[], None]) -> float:
    """Median latency in us, or NaN if the configuration does not compile."""
    try:
        fn()
        torch.accelerator.synchronize()
        return triton.testing.do_bench_cudagraph(fn, rep=200) * 1000.0
    except Exception as exc:  # noqa: BLE001 - report and keep sweeping
        print(f"  skipped ({type(exc).__name__}: {exc})")
        return float("nan")


def _fmt(value: float, fmt: str = ".1f") -> str:
    return "-" if value != value else format(value, fmt)


def _print_table(title: str, header: list[str], rows: list[list[str]]) -> None:
    widths = [
        max(len(header[i]), max((len(r[i]) for r in rows), default=0))
        for i in range(len(header))
    ]
    print(f"\n=== {title} ===")
    print("  ".join(h.rjust(w) for h, w in zip(header, widths)))
    for row in rows:
        print("  ".join(c.rjust(w) for c, w in zip(row, widths)))


def _make_ds_mla_cache(
    num_tokens: int, block_size: int, use_fnuz: bool, device: torch.device
) -> torch.Tensor:
    from vllm.models.deepseek_v4.common.ops.cache_utils import (
        quantize_and_insert_k_cache,
    )

    num_blocks = max(1, triton.cdiv(num_tokens, block_size))
    cache = torch.zeros(
        (num_blocks, block_size, CACHE_ENTRY_BYTES), dtype=torch.uint8, device=device
    )
    k = torch.randn(num_tokens, 512, dtype=torch.bfloat16, device=device)
    slots = torch.arange(num_tokens, dtype=torch.int64, device=device)
    quantize_and_insert_k_cache(
        k, cache, slots, block_size=block_size, use_fnuz=use_fnuz
    )
    return cache


def _ragged_indices(
    num_queries: int,
    seg_len: int,
    num_rows: int,
    scattered: bool,
    device: torch.device,
) -> tuple[torch.Tensor, torch.Tensor]:
    """Ragged (indices, indptr) with ``seg_len`` slots per query.

    ``scattered`` models the compressed top-k gather (random rows); contiguous
    models the SWA window.
    """
    if scattered:
        indices = torch.randint(
            0, num_rows, (num_queries * seg_len,), dtype=torch.int32, device=device
        )
    else:
        starts = torch.randint(
            0, max(1, num_rows - seg_len), (num_queries, 1), device=device
        )
        indices = (starts + torch.arange(seg_len, device=device)).to(torch.int32)
        indices = indices.reshape(-1)
    indptr = torch.arange(
        0, num_queries * seg_len + 1, seg_len, dtype=torch.int32, device=device
    )
    return indices.contiguous(), indptr


# ---------------------------------------------------------------------------
# Sparse MLA decode: single-pass vs split-K partial+reduce
# ---------------------------------------------------------------------------


def _decode_inputs(batch: int, splits: list[int], device: torch.device) -> dict:
    from vllm.platforms import current_platform
    from vllm.v1.attention.ops.fp8_sm80 import get_e4m3fn_bf16_lut

    swa_rows = 4096
    topk_rows = 128 * 1024
    is_fnuz = current_platform.is_fp8_fnuz()
    main_indices, main_indptr = _ragged_indices(batch, SWA_LEN, swa_rows, False, device)
    extra_indices, extra_indptr = _ragged_indices(
        batch, TOPK_LEN, topk_rows, True, device
    )
    q = torch.randn(batch, NUM_HEADS, HEAD_DIM, dtype=torch.bfloat16, device=device)
    part = {
        s: (
            torch.empty((batch, s, NUM_HEADS), dtype=torch.float32, device=device),
            torch.empty((batch, s, NUM_HEADS), dtype=torch.float32, device=device),
            torch.empty(
                (batch, s, NUM_HEADS, HEAD_DIM), dtype=torch.float32, device=device
            ),
        )
        for s in splits
    }
    return dict(
        q=q,
        out=torch.empty_like(q),
        main_cache=_make_ds_mla_cache(swa_rows, CACHE_BLOCK_SIZE, is_fnuz, device),
        extra_cache=_make_ds_mla_cache(topk_rows, CACHE_BLOCK_SIZE, False, device),
        main_indices=main_indices,
        main_indptr=main_indptr,
        extra_indices=extra_indices,
        extra_indptr=extra_indptr,
        attn_sink=torch.randn(NUM_HEADS, dtype=torch.float32, device=device),
        fp8_lut=get_e4m3fn_bf16_lut(device),
        is_fnuz=is_fnuz,
        part=part,
    )


def _launch_single_pass(inp: dict, block_h: int, block_k: int) -> None:
    from vllm.v1.attention.ops.rocm_aiter_mla_sparse import (
        _sparse_attn_decode_ragged_kernel,
    )

    q, out = inp["q"], inp["out"]
    main_cache, extra_cache = inp["main_cache"], inp["extra_cache"]
    _sparse_attn_decode_ragged_kernel[(q.shape[0], triton.cdiv(NUM_HEADS, block_h))](
        q,
        main_cache,
        inp["main_indices"],
        inp["main_indptr"],
        extra_cache,
        inp["extra_indices"],
        inp["extra_indptr"],
        inp["attn_sink"],
        inp["fp8_lut"],
        out,
        q.stride(0),
        q.stride(1),
        out.stride(0),
        out.stride(1),
        main_cache.stride(0),
        extra_cache.stride(0),
        main_cache.shape[0] * main_cache.shape[1],
        extra_cache.shape[0] * extra_cache.shape[1],
        main_cache.shape[1],
        extra_cache.shape[1],
        SCALE,
        NUM_HEADS,
        HAS_ATTN_SINK=True,
        HAS_EXTRA=True,
        NOPE_DIM=NOPE_DIM,
        NOPE_BLOCK=triton.next_power_of_2(NOPE_DIM),
        ROPE_DIM=ROPE_DIM,
        IS_FNUZ_MAIN=inp["is_fnuz"],
        IS_FNUZ_EXTRA=False,
        BLOCK_H=block_h,
        BLOCK_K=block_k,
        num_warps=8,
    )


def _launch_split_k(
    inp: dict, block_h: int, block_k: int, num_splits: int, num_warps: int
) -> None:
    from vllm.v1.attention.ops.rocm_aiter_mla_sparse import (
        _sparse_attn_decode_partial_kernel,
        _sparse_attn_decode_reduce_kernel,
    )

    q, out = inp["q"], inp["out"]
    part_m, part_l, part_acc = inp["part"][num_splits]
    main_cache, extra_cache = inp["main_cache"], inp["extra_cache"]
    _sparse_attn_decode_partial_kernel[
        (q.shape[0], num_splits, triton.cdiv(NUM_HEADS, block_h))
    ](
        q,
        main_cache,
        inp["main_indices"],
        inp["main_indptr"],
        extra_cache,
        inp["extra_indices"],
        inp["extra_indptr"],
        part_m,
        part_l,
        part_acc,
        inp["fp8_lut"],
        q.stride(0),
        q.stride(1),
        main_cache.stride(0),
        extra_cache.stride(0),
        part_m.stride(0),
        part_m.stride(1),
        part_acc.stride(0),
        part_acc.stride(1),
        part_acc.stride(2),
        main_cache.shape[0] * main_cache.shape[1],
        extra_cache.shape[0] * extra_cache.shape[1],
        main_cache.shape[1],
        extra_cache.shape[1],
        SCALE,
        NUM_HEADS,
        HAS_EXTRA=True,
        NOPE_DIM=NOPE_DIM,
        NOPE_BLOCK=triton.next_power_of_2(NOPE_DIM),
        ROPE_DIM=ROPE_DIM,
        IS_FNUZ_MAIN=inp["is_fnuz"],
        IS_FNUZ_EXTRA=False,
        BLOCK_H=block_h,
        BLOCK_K=block_k,
        NUM_SPLITS=num_splits,
        NUM_STAGES=1,
        num_warps=num_warps,
    )
    _sparse_attn_decode_reduce_kernel[(q.shape[0], NUM_HEADS)](
        part_m,
        part_l,
        part_acc,
        inp["attn_sink"],
        out,
        out.stride(0),
        out.stride(1),
        part_m.stride(0),
        part_m.stride(1),
        part_acc.stride(0),
        part_acc.stride(1),
        part_acc.stride(2),
        NUM_HEADS,
        HAS_ATTN_SINK=True,
        COMB_DIM=HEAD_DIM,
        BLOCK_H=1,
        NUM_SPLITS=num_splits,
        SPLITS_PAD=triton.next_power_of_2(num_splits),
        num_warps=4,
    )


def bench_sparse_decode(
    batches: list[int],
    block_hs: list[int],
    splits: list[int],
    warps: list[int],
    device: torch.device,
) -> None:
    rows = []
    for batch in batches:
        inp = _decode_inputs(batch, splits, device)
        for block_h in block_hs:
            heads_blocks = triton.cdiv(NUM_HEADS, block_h)
            variants: list[tuple[str, int, Callable[[], None]]] = [
                (
                    "single-pass",
                    batch * heads_blocks,
                    partial(_launch_single_pass, inp, block_h, 32),
                )
            ]
            variants += [
                (
                    f"split-k s{s} w{w}",
                    batch * s * heads_blocks,
                    partial(_launch_split_k, inp, block_h, 32, s, w),
                )
                for s in splits
                for w in warps
            ]
            for label, ctas, fn in variants:
                rows.append(
                    [
                        str(batch),
                        str(block_h),
                        label,
                        str(ctas),
                        _fmt(_time_us(fn)),
                    ]
                )
    _print_table(
        f"sparse MLA decode (heads={NUM_HEADS}, swa={SWA_LEN}, topk={TOPK_LEN})",
        ["batch", "block_h", "impl", "CTAs", "us"],
        rows,
    )


# ---------------------------------------------------------------------------
# mHC prenorm GEMM: [T, hc_mult*hidden] x [24, hc_mult*hidden]^T
# ---------------------------------------------------------------------------


def _torch_prenorm(
    x: torch.Tensor, fn: torch.Tensor, out: torch.Tensor, sqrsum: torch.Tensor
) -> None:
    x_wide = x if fn.dtype == torch.bfloat16 else x.float()
    out[0].copy_(x_wide @ fn.t())
    sqrsum[0].copy_(x.float().square().sum(-1))


def bench_prenorm_gemm(
    tokens: list[int], configs: list[tuple[int, int]], device: torch.device
) -> None:
    from vllm.model_executor.kernels.mhc.tilelang_kernels import (
        hc_prenorm_gemm_block_m_tilelang,
        hc_prenorm_gemm_tilelang,
    )

    k = HC_MULT * HIDDEN_SIZE
    fn = torch.randn(HC_MULT3, k, dtype=torch.float32, device=device)
    fn_bf16 = fn.to(torch.bfloat16)
    rows = []
    for num_tokens in tokens:
        x = torch.randn(num_tokens, k, dtype=torch.bfloat16, device=device)
        out = torch.empty(1, num_tokens, HC_MULT3, dtype=torch.float32, device=device)
        sqrsum = torch.empty(1, num_tokens, dtype=torch.float32, device=device)
        # fn dominates: it is re-read by every CTA that owns a token tile.
        bytes_min = x.numel() * 2 + fn.numel() * 4
        variants: list[tuple[str, str, Callable[[], None]]] = [
            (
                "tilelang",
                "split-1",
                partial(
                    hc_prenorm_gemm_tilelang,
                    x,
                    fn,
                    out,
                    sqrsum,
                    HIDDEN_SIZE,
                    HC_MULT,
                    HC_MULT3,
                    512,
                    12,
                    1,
                ),
            )
        ]
        # `fn` traffic scales 1/block_m, `x` traffic 1/tile_n; registers run
        # ~block_m*tile_n + block_m + tile_n + 20 against a 128-reg ceiling, so
        # the pair must move together. (8, 12) is expected to fail to launch.
        variants += [
            (
                "tilelang",
                f"block_m={m},tile_n={t}",
                partial(
                    hc_prenorm_gemm_block_m_tilelang,
                    x,
                    fn,
                    out,
                    sqrsum,
                    HIDDEN_SIZE,
                    HC_MULT,
                    HC_MULT3,
                    512,
                    t,
                    m,
                ),
            )
            for m, t in configs
        ]
        # Reference routes for the fp32 -> bf16 tensor-core question.
        variants += [
            ("torch", "fp32", partial(_torch_prenorm, x, fn, out, sqrsum)),
            ("torch", "bf16", partial(_torch_prenorm, x, fn_bf16, out, sqrsum)),
        ]
        for impl, cfg, fn_ in variants:
            us = _time_us(fn_)
            gbs = float("nan") if us != us else bytes_min / (us * 1e-6) / 1e9
            rows.append([str(num_tokens), impl, cfg, _fmt(us), _fmt(gbs, ".0f")])
    _print_table(
        f"mHC prenorm GEMM (K={k}, N={HC_MULT3}, fp32 weight)",
        ["tokens", "impl", "cfg", "us", "GB/s"],
        rows,
    )


# ---------------------------------------------------------------------------
# mHC pre big-fuse. The grid is one CTA per token, but widening the worker warps
# was measured to do nothing (8.33 us at both 64 and 256 workers at batch 1):
# warp 0 walks `sinkhorn_repeat` dependent 4x4 normalizations serially and is the
# critical path. This sweeps that count to keep the attribution honest -- the
# difference against repeat=1 is the addressable share.
# ---------------------------------------------------------------------------


def bench_mhc_pre(
    tokens: list[int], sinkhorn_iters: list[int], device: torch.device
) -> None:
    from vllm.model_executor.kernels.mhc.tilelang_kernels import (
        mhc_pre_big_fuse_with_norm_tilelang,
    )

    n_splits = 1
    rows = []
    for num_tokens in tokens:
        tensors = (
            torch.randn(
                n_splits, num_tokens, HC_MULT3, dtype=torch.float32, device=device
            ),
            torch.rand(n_splits, num_tokens, dtype=torch.float32, device=device) + 1.0,
            torch.randn(3, dtype=torch.float32, device=device),
            torch.randn(HC_MULT3, dtype=torch.float32, device=device),
            torch.randn(
                num_tokens, HC_MULT, HIDDEN_SIZE, dtype=torch.bfloat16, device=device
            ),
            torch.empty(num_tokens, HC_MULT, dtype=torch.float32, device=device),
            torch.empty(
                num_tokens, HC_MULT * HC_MULT, dtype=torch.float32, device=device
            ),
            torch.empty(num_tokens, HIDDEN_SIZE, dtype=torch.bfloat16, device=device),
            torch.randn(HIDDEN_SIZE, dtype=torch.bfloat16, device=device),
        )
        # residual read + normed layer_input write
        moved = num_tokens * HIDDEN_SIZE * 2 * (HC_MULT + 1)
        for iters in sinkhorn_iters:
            us = _time_us(
                partial(
                    mhc_pre_big_fuse_with_norm_tilelang,
                    *tensors,
                    HIDDEN_SIZE,
                    1e-6,
                    1e-6,
                    1e-6,
                    2.0,
                    iters,
                    1e-6,
                    n_splits,
                    HC_MULT,
                )
            )
            gbs = float("nan") if us != us else moved / (us * 1e-6) / 1e9
            label = f"{iters} (checkpoint)" if iters == SINKHORN_ITERS else str(iters)
            rows.append(
                [
                    str(num_tokens),
                    label,
                    _fmt(us),
                    _fmt(us * MHC_PRE_LAUNCHES_PER_STEP / 1000, ".3f"),
                    _fmt(gbs, ".0f"),
                ]
            )
    _print_table(
        f"mHC pre big-fuse + norm (hidden={HIDDEN_SIZE}, hc_mult={HC_MULT}); "
        f"ms/step assumes {MHC_PRE_LAUNCHES_PER_STEP} launches/step",
        ["tokens", "sinkhorn_iters", "us", "ms/step", "GB/s"],
        rows,
    )


# ---------------------------------------------------------------------------
# Prefill K-cache dequantize + gather
# ---------------------------------------------------------------------------


def _launch_dequant_gather(
    out: torch.Tensor,
    cache: torch.Tensor,
    seq_lens: torch.Tensor,
    block_table: torch.Tensor,
    num_workers: int,
) -> None:
    from vllm.models.deepseek_v4.common.ops.cache_utils import (
        _dequantize_and_gather_k_kernel,
    )

    _dequantize_and_gather_k_kernel[(seq_lens.shape[0], num_workers)](
        out,
        out.stride(0),
        out.stride(1),
        cache,
        seq_lens,
        block_table,
        0,
        None,
        max_blocks_per_seq=block_table.shape[-1],
        fp8_dim=NOPE_DIM,
        bf16_dim=ROPE_DIM,
        scale_dim=SCALE_DIM,
        quant_block=QUANT_BLOCK,
        cache_block_size=CACHE_BLOCK_SIZE,
        token_data_size=CACHE_TOKEN_BYTES,
        block_stride=cache.stride(0),
        output_dim=512,
        fp8_max=448.0,
        fp8_block=triton.next_power_of_2(NOPE_DIM),
        use_fnuz=False,
    )


def bench_dequant_gather(
    gather_lens: list[int],
    num_reqs_list: list[int],
    workers: list[int],
    device: torch.device,
) -> None:
    rows = []
    for num_reqs, gather_len in itertools.product(num_reqs_list, gather_lens):
        cache = _make_ds_mla_cache(gather_len, CACHE_BLOCK_SIZE, False, device)
        blocks_per_seq = triton.cdiv(gather_len, CACHE_BLOCK_SIZE)
        block_table = (
            torch.arange(blocks_per_seq, dtype=torch.int32, device=device)
            .repeat(num_reqs, 1)
            .contiguous()
        )
        seq_lens = torch.full((num_reqs,), gather_len, dtype=torch.int32, device=device)
        out = torch.empty(
            num_reqs, gather_len, 512, dtype=torch.bfloat16, device=device
        )
        moved = num_reqs * gather_len * (CACHE_ENTRY_BYTES + 512 * 2)
        for num_workers in workers:
            us = _time_us(
                partial(
                    _launch_dequant_gather,
                    out,
                    cache,
                    seq_lens,
                    block_table,
                    num_workers,
                )
            )
            gbs = float("nan") if us != us else moved / (us * 1e-6) / 1e9
            rows.append(
                [
                    str(num_reqs),
                    str(gather_len),
                    str(num_workers),
                    _fmt(us),
                    _fmt(gbs, ".0f"),
                ]
            )
    _print_table(
        "dequantize_and_gather_k_cache (Triton)",
        ["reqs", "gather_len", "workers", "us", "GB/s"],
        rows,
    )


KERNELS = ("sparse-decode", "prenorm-gemm", "mhc-pre", "dequant-gather")

# What a batch-1 decode step is made of, and where each part can be timed. This
# exists so that summing the sweeps above is never mistaken for a decomposition
# of the whole step: the covered rows are a minority of decode time, and a total
# that silently omits Marlin and MoE would understate the step by roughly half.
_DECODE_COVERAGE = [
    ("sparse-MLA decode", "~18%", "here: --kernel sparse-decode"),
    ("mHC pre big-fuse", "~6%", "here: --kernel mhc-pre"),
    ("dense Marlin fp8", "~26%", "benchmarks/kernels/benchmark_marlin.py"),
    ("MoE", "~10%", "benchmarks/kernels/benchmark_moe.py"),
    ("cuBLAS GEMV", "~13%", "not covered: plain torch matmul at M=1"),
    ("indexer MQA logits", "~11%", "NOT COVERED - needs a paged indexer cache"),
    ("mHC post / fused-post-pre", "~3%", "NOT COVERED"),
    ("norms, RoPE, elementwise", "rest", "NOT COVERED - ~235 small launches"),
]


def print_decode_coverage() -> None:
    _print_table(
        "batch-1 decode coverage (shares are relative, from the c1 decode trace)",
        ["component", "share", "where to measure"],
        [list(row) for row in _DECODE_COVERAGE],
    )
    print(
        "\nDo not sum only the covered rows and call it a step budget -- see the\n"
        "NOT COVERED entries above."
    )


def _int_list(value: str) -> list[int]:
    return [int(v) for v in value.split(",")]


def _pair_list(value: str) -> list[tuple[int, int]]:
    """Parse "8x4,8x6" into [(8, 4), (8, 6)]."""
    pairs = []
    for item in value.split(","):
        a, _, b = item.partition("x")
        pairs.append((int(a), int(b)))
    return pairs


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--kernel", choices=(*KERNELS, "all"), default="all")
    parser.add_argument(
        "--coverage",
        action="store_true",
        help="print what a batch-1 decode step is made of and exit",
    )
    parser.add_argument("--batches", type=_int_list, default=[1, 8, 32])
    parser.add_argument("--block-h", type=_int_list, default=[16, 8, 4, 2])
    parser.add_argument("--splits", type=_int_list, default=[1, 4, 8, 16, 32, 64])
    parser.add_argument("--warps", type=_int_list, default=[4, 8])
    parser.add_argument("--tokens", type=_int_list, default=[1, 8, 32, 128, 512, 2048])
    parser.add_argument(
        "--prenorm-configs",
        type=_pair_list,
        default=[(2, 12), (4, 8), (8, 4), (8, 6), (8, 12)],
        help="block_m x tile_n pairs, e.g. 8x4,8x6",
    )
    parser.add_argument(
        "--sinkhorn-iters", type=_int_list, default=[1, 5, 10, SINKHORN_ITERS]
    )
    parser.add_argument("--gather-lens", type=_int_list, default=[2176, 8192, 32768])
    parser.add_argument("--gather-reqs", type=_int_list, default=[1, 4])
    parser.add_argument(
        "--gather-workers", type=_int_list, default=[128, 256, 512, 1024, 2048]
    )
    args = parser.parse_args()

    if args.coverage:
        print_decode_coverage()
        return

    torch.manual_seed(0)
    device = torch.device("cuda")
    selected = KERNELS if args.kernel == "all" else (args.kernel,)

    if "sparse-decode" in selected:
        bench_sparse_decode(args.batches, args.block_h, args.splits, args.warps, device)
    if "prenorm-gemm" in selected:
        bench_prenorm_gemm(args.tokens, args.prenorm_configs, device)
    if "mhc-pre" in selected:
        bench_mhc_pre(args.tokens, args.sinkhorn_iters, device)
    if "dequant-gather" in selected:
        bench_dequant_gather(
            args.gather_lens, args.gather_reqs, args.gather_workers, device
        )


if __name__ == "__main__":
    main()
