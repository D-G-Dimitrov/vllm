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

from vllm.triton_utils import tl, triton

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
CFG_N_ROUTED_EXPERTS = 256  # n_routed_experts
CFG_NUM_EXPERTS_PER_TOK = 6  # num_experts_per_tok
CFG_HC_MULT = 4  # hc_mult
CFG_HC_SINKHORN_ITERS = 20  # hc_sinkhorn_iters
CFG_SLIDING_WINDOW = 128  # sliding_window
CFG_INDEX_TOPK = 512  # index_topk
CFG_INDEX_N_HEADS = 64  # index_n_heads (replicated, not TP-sharded)
CFG_INDEX_HEAD_DIM = 128  # index_head_dim
CFG_Q_LORA_RANK = 1024  # q_lora_rank
CFG_O_LORA_RANK = 1024  # o_lora_rank
CFG_O_GROUPS = 8  # o_groups
CFG_MOE_INTERMEDIATE_SIZE = 2048  # moe_intermediate_size (n_shared_experts=1)
CFG_WEIGHT_BLOCK_SIZE = 128  # quantization_config.weight_block_size = [128, 128]

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


def _decode_inputs(
    batch: int,
    splits: list[int],
    device: torch.device,
    topk_len: int = TOPK_LEN,
    topk_rows: int = 26875,
    swa_rows: int = 4096,
) -> dict:
    """Decode inputs matching the live caller: SWA is the *main* segment
    (contiguous window) and the compressed top-k is *extra* (scattered) --
    see `rocm_sparse_attn_decode`, which passes `main_cache=swa_k_cache,
    main_lengths=swa_lens` and `extra_cache=kv_cache, extra_lengths=topk_lens`.

    ``topk_rows`` is the row count the scattered gather indexes into, and it
    is the single most misleading knob here. It used to be hardcoded at
    128*1024 rows = 76.6 MB of fp8_ds_mla cache against an A100's 40 MB L2,
    so every measurement was taken in a DRAM-bound regime the server never
    enters: serving gathers out of ctx/compress_ratio rows, which is 4.8 MB
    at 32k and 19.1 MB at 128k -- L2-resident throughout. That inflated the
    kernel roughly 2.6x against the live 17.30 us and is why bench-derived
    per-call numbers disagreed with the trace.
    """
    from vllm.platforms import current_platform
    from vllm.v1.attention.ops.fp8_sm80 import get_e4m3fn_bf16_lut

    is_fnuz = current_platform.is_fp8_fnuz()
    main_indices, main_indptr = _ragged_indices(batch, SWA_LEN, swa_rows, False, device)
    extra_indices, extra_indptr = _ragged_indices(
        batch, topk_len, topk_rows, True, device
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
    topk_len: int = TOPK_LEN,
    topk_rows: int = 26875,
) -> None:
    from vllm.v1.attention.ops.rocm_aiter_mla_sparse import _decode_num_splits

    rows = []
    for batch in batches:
        for block_h in block_hs:
            heads_blocks = triton.cdiv(NUM_HEADS, block_h)
            # Serving picks the split count from the same heuristic, off the
            # real segment lengths; at batch 1 that is 16, not the 8 the
            # default list leads with. Comparing arms at a split count serving
            # never uses reads a different delta, so mark the live one.
            live_splits = _decode_num_splits(
                batch, heads_blocks, float(SWA_LEN), float(topk_len), 32
            )
            all_splits = sorted({*splits, live_splits})
            inp = _decode_inputs(batch, all_splits, device, topk_len, topk_rows)
            variants: list[tuple[str, int, Callable[[], None]]] = [
                (
                    "single-pass",
                    batch * heads_blocks,
                    partial(_launch_single_pass, inp, block_h, 32),
                )
            ]
            variants += [
                (
                    f"split-k s{s} w{w}" + (" (live)" if s == live_splits else ""),
                    batch * s * heads_blocks,
                    partial(_launch_split_k, inp, block_h, 32, s, w),
                )
                for s in all_splits
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
        f"sparse MLA decode (heads={NUM_HEADS}, swa={SWA_LEN}, topk={topk_len}, "
        f"gather pool={topk_rows} rows = "
        f"{topk_rows * CACHE_ENTRY_BYTES / 2**20:.1f} MB)",
        ["batch", "block_h", "impl", "CTAs", "us"],
        rows,
    )


# ---------------------------------------------------------------------------
# Sparse MLA prefill: reported at 17.9% occupancy, capped at 3 CTAs/SM by BOTH
# 168 regs/thread and 49,664 B smem. Both figures are trace metadata, so this
# mode reads registers, spills and smem off the compiled kernel instead and
# prints which of the two caps actually binds at each config.
# ---------------------------------------------------------------------------

# A100 (SM80) per-SM limits. sharedMemPerMultiprocessor is 164 KB; a single
# block may opt into at most 163 KB of it.
_SM80_REGS_PER_SM = 65536
_SM80_SMEM_PER_SM = 164 * 1024
_SM80_WARPS_PER_SM = 64


def _occupancy(n_regs: int, shared: int, num_warps: int) -> tuple[int, str, float]:
    """CTAs/SM, which resource caps it, and warp occupancy."""
    threads = 32 * num_warps
    # Registers are allocated per warp in granular chunks; the per-thread
    # figure times the thread count is the closest an outside model can get,
    # so treat a tie as "both" rather than pretending to resolve it.
    by_regs = _SM80_REGS_PER_SM // max(1, n_regs * threads)
    by_smem = _SM80_SMEM_PER_SM // max(1, shared) if shared else 32
    ctas = max(0, min(by_regs, by_smem, 32))
    if by_regs < by_smem:
        binder = "regs"
    elif by_smem < by_regs:
        binder = "smem"
    else:
        binder = "both"
    return ctas, binder, 100.0 * ctas * num_warps / _SM80_WARPS_PER_SM


def _prefill_inputs(m_tokens: int, ctx: int, kv_len: int, device: torch.device) -> dict:
    """One chunk of ragged sparse prefill: every query gathers ``kv_len``
    scattered rows out of a ``ctx``-row KV pool, which is the loaded case --
    a chunk row late in a long context attends its full top-k."""
    indices = torch.randint(
        0, ctx, (m_tokens * kv_len,), dtype=torch.int32, device=device
    )
    indptr = torch.arange(
        0, m_tokens * kv_len + 1, kv_len, dtype=torch.int32, device=device
    )
    return dict(
        q=torch.randn(
            m_tokens, NUM_HEADS, HEAD_DIM, dtype=torch.bfloat16, device=device
        ),
        kv=torch.randn(ctx, HEAD_DIM, dtype=torch.bfloat16, device=device),
        indices=indices,
        indptr=indptr,
        attn_sink=torch.randn(NUM_HEADS, dtype=torch.float32, device=device),
    )


def _launch_sparse_prefill(
    inp: dict,
    block_h: int,
    block_k: int,
    num_warps: int,
    maxnreg: int,
    num_stages: int,
    out: torch.Tensor,
) -> object:
    from vllm.v1.attention.ops.rocm_aiter_mla_sparse import (
        _sparse_attn_prefill_ragged_kernel,
    )

    q, kv = inp["q"], inp["kv"]
    extra = {"maxnreg": maxnreg} if maxnreg else {}
    # num_stages=0 means "pass nothing", i.e. Triton's default -- which is what
    # the serving launch does. It is not the same as num_stages=1: the default
    # pipelines to 49,664 B of smem, the exact figure the trace reported, while
    # 1 compiles a different (slower) kernel. Benchmarking against 1 would
    # invent a win that production already has.
    if num_stages:
        extra["num_stages"] = num_stages
    return _sparse_attn_prefill_ragged_kernel[
        (q.shape[0], triton.cdiv(NUM_HEADS, block_h))
    ](
        q,
        kv,
        inp["indices"],
        inp["indptr"],
        inp["attn_sink"],
        out,
        q.stride(0),
        q.stride(1),
        q.stride(2),
        kv.stride(0),
        kv.stride(1),
        out.stride(0),
        out.stride(1),
        out.stride(2),
        NUM_HEADS,
        HEAD_DIM,
        kv.shape[0],
        HEAD_DIM**-0.5,
        HAS_ATTN_SINK=True,
        BLOCK_H=block_h,
        BLOCK_D=triton.next_power_of_2(HEAD_DIM),
        BLOCK_K=block_k,
        num_warps=num_warps,
        **extra,
    )


def bench_sparse_prefill(
    ms: list[int],
    ctx_ns: list[int],
    block_hs: list[int],
    block_ks: list[int],
    warps: list[int],
    maxnregs: list[int],
    stages: list[int],
    device: torch.device,
) -> None:
    rows = []
    for m_tokens, ctx in itertools.product(ms, ctx_ns):
        kv_len = min(TOPK_LEN, ctx)
        inp = _prefill_inputs(m_tokens, ctx, kv_len, device)
        out = torch.empty_like(inp["q"])
        for block_h, block_k, num_warps, maxnreg, num_stages in itertools.product(
            block_hs, block_ks, warps, maxnregs, stages
        ):
            fn = partial(
                _launch_sparse_prefill,
                inp,
                block_h,
                block_k,
                num_warps,
                maxnreg,
                num_stages,
                out,
            )
            n_regs = n_spills = shared = 0
            try:
                compiled = fn()
                torch.accelerator.synchronize()
                n_regs = getattr(compiled, "n_regs", 0)
                n_spills = getattr(compiled, "n_spills", 0)
                shared = getattr(compiled, "metadata", None)
                shared = getattr(shared, "shared", 0) if shared else 0
            except Exception as exc:  # noqa: BLE001 - report and keep sweeping
                print(f"  skipped ({type(exc).__name__}: {exc})")
            ctas, binder, occ = _occupancy(n_regs, shared, num_warps)
            rows.append(
                [
                    str(m_tokens),
                    str(ctx),
                    str(block_h),
                    str(block_k),
                    str(num_warps),
                    str(maxnreg) if maxnreg else "-",
                    str(num_stages) if num_stages else "def",
                    str(n_regs),
                    str(n_spills),
                    str(shared),
                    f"{ctas} ({binder})",
                    _fmt(occ),
                    _fmt(_time_us(fn)),
                ]
            )
    _print_table(
        f"sparse MLA prefill (heads={NUM_HEADS}, D={HEAD_DIM}, topk={TOPK_LEN})",
        [
            "M",
            "ctx",
            "bH",
            "bK",
            "warps",
            "maxnreg",
            "stages",
            "regs",
            "spill",
            "smem",
            "CTA/SM",
            "occ%",
            "us",
        ],
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
        # The production cuBLAS route: bf16 GEMM + one-pass Triton sqrsum.
        from vllm.model_executor.kernels.mhc.triton import hc_prenorm_gemm_cublas

        variants += [
            (
                "cublas",
                "gemm+sqrsum",
                partial(hc_prenorm_gemm_cublas, x, fn, out, sqrsum),
            )
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


# ---------------------------------------------------------------------------
# Indexer MQA logits (prefill). Register-limited: 132 regs/thread caps 3 CTAs/SM
# and Compute Warps in Flight sits at ~96% of that ceiling, so `maxnreg` is the
# knob this sweep exposes (128 is exactly the 4th-CTA/SM boundary at 128
# threads). Per-CTA cost is context-independent, so one long-N point per M is
# representative of any context length.
# ---------------------------------------------------------------------------


_LOGITS_BLOCK_N = 128  # production autotune space is BLOCK_N=128 only


def _launch_indexer_logits(
    inp: dict,
    grid: tuple[int, int],
    n_ctx: int,
    maxnreg: int,
    num_stages: int,
    kv_group: int,
) -> None:
    from vllm.v1.attention.ops.mqa_logits_triton import _fp8_mqa_logits_kernel

    # Bypass @triton.autotune via .fn so maxnreg is an explicit knob.
    extra = {"maxnreg": maxnreg} if maxnreg else {}
    q, k, weights, logits = inp["q"], inp["k"], inp["weights"], inp["logits"]
    _fp8_mqa_logits_kernel.fn[grid](
        q,
        k,
        inp["k_scales"],
        weights,
        inp["ks"],
        inp["ke"],
        logits,
        q.stride(0),
        q.stride(1),
        q.stride(2),
        k.stride(0),
        k.stride(1),
        weights.stride(0),
        weights.stride(1),
        logits.stride(0),
        logits.stride(1),
        num_heads=CFG_INDEX_N_HEADS,
        head_dim=CFG_INDEX_HEAD_DIM,
        N=n_ctx,
        BLOCK_H=max(16, triton.next_power_of_2(CFG_INDEX_N_HEADS)),
        BLOCK_D=triton.next_power_of_2(CFG_INDEX_HEAD_DIM),
        BLOCK_N=_LOGITS_BLOCK_N,
        KV_GROUP=kv_group,
        num_warps=4,
        num_stages=num_stages,
        **extra,
    )


def bench_indexer_logits(
    ms: list[int],
    ctx_ns: list[int],
    maxnregs: list[int],
    stages: list[int],
    kv_groups: list[int],
    device: torch.device,
) -> None:
    rows = []
    for m_tokens, n_ctx in itertools.product(ms, ctx_ns):
        inp = dict(
            q=torch.randn(
                m_tokens,
                CFG_INDEX_N_HEADS,
                CFG_INDEX_HEAD_DIM,
                dtype=torch.bfloat16,
                device=device,
            ),
            k=torch.randn(
                n_ctx, CFG_INDEX_HEAD_DIM, dtype=torch.bfloat16, device=device
            ),
            k_scales=torch.rand(n_ctx, dtype=torch.float32, device=device) + 0.5,
            weights=torch.rand(
                m_tokens, CFG_INDEX_N_HEADS, dtype=torch.float32, device=device
            ),
            # Full [0, N) range per row: at long context nearly every chunk row
            # attends the whole compressed prefix, so this is the loaded case
            # the trace measured, not an adversarial one.
            ks=torch.zeros(m_tokens, dtype=torch.int32, device=device),
            ke=torch.full((m_tokens,), n_ctx, dtype=torch.int32, device=device),
            logits=torch.empty(m_tokens, n_ctx, dtype=torch.float32, device=device),
        )
        for maxnreg, num_stages, kv_group in itertools.product(
            maxnregs, stages, kv_groups
        ):
            grid = (m_tokens, triton.cdiv(n_ctx, _LOGITS_BLOCK_N * kv_group))
            us = _time_us(
                partial(
                    _launch_indexer_logits,
                    inp,
                    grid,
                    n_ctx,
                    maxnreg,
                    num_stages,
                    kv_group,
                )
            )
            ns_per_cta = float("nan") if us != us else us * 1e3 / (grid[0] * grid[1])
            rows.append(
                [
                    str(m_tokens),
                    str(n_ctx),
                    str(maxnreg) if maxnreg else "-",
                    str(num_stages),
                    str(kv_group),
                    _fmt(us),
                    _fmt(ns_per_cta, ".1f"),
                ]
            )
    _print_table(
        f"indexer MQA logits (H={CFG_INDEX_N_HEADS}, D={CFG_INDEX_HEAD_DIM}, "
        f"BLOCK_N={_LOGITS_BLOCK_N}, num_warps=4)",
        ["M", "N", "maxnreg", "stages", "G", "us", "ns/CTA"],
        rows,
    )


# ---------------------------------------------------------------------------
# The decode tail: ~130 launches/step of small elementwise/reduction kernels
# running at 1-2 CTAs. Whether widening their grids can pay is decided by one
# number -- how much of each launch sits above the floor that any kernel node
# costs -- so this arm measures the floor first and reports every kernel as a
# multiple of it. Timed under cudagraph replay because that is how decode runs
# them; an eager loop measures host dispatch instead.
# ---------------------------------------------------------------------------


def _graph_time_us(fn: Callable[[], object], reps: int = 50) -> float:
    for _ in range(10):
        fn()
    torch.accelerator.synchronize()
    graph = torch.cuda.CUDAGraph()
    with torch.cuda.graph(graph):
        for _ in range(reps):
            fn()
    for _ in range(5):
        graph.replay()
    torch.accelerator.synchronize()
    start, end = torch.cuda.Event(True), torch.cuda.Event(True)
    start.record()
    for _ in range(20):
        graph.replay()
    end.record()
    torch.accelerator.synchronize()
    return start.elapsed_time(end) / (20 * reps) * 1000


def bench_tail_launch(ms: list[int], device: torch.device) -> None:
    import vllm._custom_ops as ops

    tiny = torch.zeros(1, device=device)
    floor = _graph_time_us(lambda: tiny.add_(1.0))

    rows = []
    for m in ms:
        for label, dim in (("hidden", CFG_HIDDEN_SIZE), ("q_lora", CFG_Q_LORA_RANK)):
            x = torch.randn(m, dim, dtype=torch.bfloat16, device=device)
            w = torch.randn(dim, dtype=torch.bfloat16, device=device)
            out = torch.empty_like(x)
            res = torch.randn_like(x)
            # Call the fused ops directly: an RMSNorm module built outside a
            # real engine silently falls back to the native PyTorch composite
            # ("Priority not set for op rms_norm"), which is several kernels
            # and ~10x slower than what production runs.
            for name, fn in (
                (
                    f"rms_norm {label}",
                    lambda out=out, x=x, w=w: ops.rms_norm(out, x, w, 1e-6),
                ),
                (
                    f"fused_add_rms_norm {label}",
                    lambda x=x, res=res, w=w: ops.fused_add_rms_norm(x, res, w, 1e-6),
                ),
            ):
                us = _graph_time_us(fn)
                rows.append(
                    [
                        str(m),
                        name,
                        _fmt(us, ".2f"),
                        _fmt(us / floor, ".1f"),
                        _fmt(us - floor, ".2f"),
                    ]
                )
        src = torch.randn(
            m,
            CFG_NUM_EXPERTS_PER_TOK,
            CFG_HIDDEN_SIZE,
            dtype=torch.bfloat16,
            device=device,
        )
        dst = torch.empty(m, CFG_HIDDEN_SIZE, dtype=torch.bfloat16, device=device)
        us = _graph_time_us(lambda src=src, dst=dst: ops.moe_sum(src, dst))
        rows.append(
            [
                str(m),
                "moe_sum",
                _fmt(us, ".2f"),
                _fmt(us / floor, ".1f"),
                _fmt(us - floor, ".2f"),
            ]
        )

    _print_table(
        f"decode tail vs launch floor ({floor:.2f} us for a 1-element add)",
        ["M", "kernel", "us", "x floor", "above floor"],
        rows,
    )
    print(
        "\n'above floor' bounds what any grid change can win per launch: the\n"
        "payload is 8 KB, so what sits above the floor is fixed kernel overhead\n"
        "rather than a parallelism shortfall, and extra CTAs have nothing to do."
    )


# ---------------------------------------------------------------------------
# Unquantized bf16 GEMVs at M=1. These are the two narrow-N projections that
# stay in bf16 while everything else is block-fp8: the indexer's weights_proj
# and the MoE router gate. Both are latency items rather than bandwidth ones --
# the weights are 512 KB and 2 MB -- so what matters is launch count and how
# many CTAs the N dimension can supply.
# ---------------------------------------------------------------------------

# (name, K, N, out dtype, launches per step). Counts are per *step*, not per
# layer, because these two do not run on the same layers: the indexer is built
# only where compress_ratio == 4 (attention.py:277), which config.json puts at
# 21 layers, while every layer's ffn is a DeepseekV4MoE, so the gate runs 43x.
_BF16_GEMV_SHAPES = [
    # ReplicatedLinear(hidden_size, index_n_heads), quant_config=None -> bf16
    ("indexer.weights_proj", CFG_HIDDEN_SIZE, CFG_INDEX_N_HEADS, torch.bfloat16, 21),
    # GateLinear(hidden_size, n_routed_experts, out_dtype=fp32). On SM80 every
    # specialized tier is gated behind SM90+, so this lands on tier 6: F.linear
    # in bf16 followed by a separate .to(fp32) cast -- two launches, and the
    # fp32 output dtype is nominal because the accumulation has already been
    # rounded through bf16.
    ("moe.gate", CFG_HIDDEN_SIZE, CFG_N_ROUTED_EXPERTS, torch.float32, 43),
]


def _launch_bf16_gemv(x: torch.Tensor, w: torch.Tensor, out_dtype):
    """Exercise the shipped kernel, not a copy of it."""
    from vllm.model_executor.kernels.linear.gemv_triton import bf16_gemv

    return bf16_gemv(x, w, out_dtype)


def bench_bf16_gemv(ms: list[int], device: torch.device) -> None:
    import torch.nn.functional as F

    rows = []
    step_us: dict[str, dict[str, float]] = {}
    for m_tokens, (name, k, n, out_dtype, count) in itertools.product(
        ms, _BF16_GEMV_SHAPES
    ):
        w = torch.randn(n, k, dtype=torch.bfloat16, device=device) * 0.02
        x = torch.randn(m_tokens, k, dtype=torch.bfloat16, device=device)

        def _baseline(x=x, w=w, out_dtype=out_dtype):
            y = F.linear(x, w)
            # GateLinear tier 6 casts after the GEMM; that cast is a real
            # launch and belongs in the baseline.
            return y.to(out_dtype) if y.dtype != out_dtype else y

        ref = _baseline()
        # fp32 reference computed the way a specialized tier would, to show
        # what the bf16 round-trip costs in accuracy rather than only in time.
        exact = (x.float() @ w.float().T).flatten()

        variants: list[tuple[str, Callable[[], None]]] = [("production", _baseline)]
        variants += [("triton gemv", partial(_launch_bf16_gemv, x, w, out_dtype))]
        for label, fn in variants:
            us = _time_us(fn)
            got = fn()
            torch.accelerator.synchronize()
            got = got.float().flatten()
            rows.append(
                [
                    str(m_tokens),
                    name,
                    f"{k}x{n}",
                    label,
                    str(n),
                    _fmt(us, ".2f"),
                    f"{(got - ref.float().flatten()).abs().max().item():.1e}",
                    f"{(got - exact).abs().max().item():.1e}",
                ]
            )
            step_us.setdefault(f"M={m_tokens} {label}", {})[name] = us * count
    _print_table(
        "unquantized bf16 GEMV at M=1 (per-step launch counts)",
        ["M", "layer", "KxN", "impl", "CTAs", "us", "vs prod", "vs fp32"],
        rows,
    )
    print("\nPer-step totals (21 indexer layers + 43 gate layers):")
    for label, per_shape in sorted(step_us.items()):
        if len(per_shape) != len(_BF16_GEMV_SHAPES):
            continue
        print(f"  {label:>22}: {sum(per_shape.values()) / 1e3:.3f} ms/step")


# ---------------------------------------------------------------------------
# Dense Marlin fp8 at M=1: the largest single decode component (~3.22 ms/step,
# 28%), streaming 26.2 MB/layer of weights at ~15% of DRAM peak. Marlin runs
# 200 threads with 145 KB smem/CTA = 1 CTA/SM, and at M=1 the smem staging buys
# nothing (weights stream once, zero reuse) -- the kernel's structure is wrong
# for GEMV-shaped work. Arms: production Marlin; dequant-to-bf16 at load +
# cuBLAS (Route C control, costs +1.13 GB VRAM/rank); fused LUT/ALU-decode
# bf16 GEMV in Triton drawing parallelism from N (Route B primary).
# ---------------------------------------------------------------------------

# The six per-layer per-rank M=1 GEMM shapes that go through dense Marlin fp8
# at TP=8 (wo_a is exempt: consumed as raw block-fp8 by the attention bmm).
# (name, K, N, launches per layer); every dimension traces to config.json.
_DENSE_GEMM_SHAPES = [
    # hidden -> q_lora_rank + head_dim, fused ReplicatedLinear
    ("fused_wqa_wkv", CFG_HIDDEN_SIZE, CFG_Q_LORA_RANK + CFG_HEAD_DIM, 1),
    # q_lora_rank -> (num_attention_heads / TP) * head_dim, and
    # (o_groups * o_lora_rank) / TP -> hidden: same (K, N) at TP=8
    (
        "wq_b+wo_b",
        CFG_Q_LORA_RANK,
        CFG_NUM_ATTENTION_HEADS // TP_SIZE * CFG_HEAD_DIM,
        2,
    ),
    # q_lora_rank -> index_n_heads * index_head_dim, ReplicatedLinear
    ("indexer.wq_b", CFG_Q_LORA_RANK, CFG_INDEX_N_HEADS * CFG_INDEX_HEAD_DIM, 1),
    # hidden -> 2 * moe_intermediate_size / TP (shared expert gate_up)
    ("shared_gate_up", CFG_HIDDEN_SIZE, 2 * CFG_MOE_INTERMEDIATE_SIZE // TP_SIZE, 1),
    # moe_intermediate_size / TP -> hidden (shared expert down)
    ("shared_down", CFG_MOE_INTERMEDIATE_SIZE // TP_SIZE, CFG_HIDDEN_SIZE, 1),
]


def _fp8_block_quant(
    w: torch.Tensor, qb: int = CFG_WEIGHT_BLOCK_SIZE
) -> tuple[torch.Tensor, torch.Tensor]:
    """Quantize a (N, K) bf16 weight to block-fp8 exactly like the checkpoint:
    one fp32 scale per qb x qb block, e4m3 payload."""
    n, k = w.shape
    assert n % qb == 0 and k % qb == 0
    wv = w.float().view(n // qb, qb, k // qb, qb)
    amax = wv.abs().amax(dim=(1, 3), keepdim=True).clamp(min=1e-12)
    scales = amax / 448.0
    q = (wv / scales).clamp(-448.0, 448.0)
    w_fp8 = q.view(n, k).to(torch.float8_e4m3fn)
    return w_fp8, scales.view(n // qb, k // qb).contiguous()


def _fp8_block_dequant(w_fp8: torch.Tensor, scales: torch.Tensor) -> torch.Tensor:
    qb = CFG_WEIGHT_BLOCK_SIZE
    n, k = w_fp8.shape
    wv = w_fp8.float().view(n // qb, qb, k // qb, qb)
    return (wv * scales.view(n // qb, 1, k // qb, 1)).view(n, k).bfloat16()


def _make_marlin_layer(
    w_fp8: torch.Tensor, scales: torch.Tensor, device: torch.device
) -> torch.nn.Module:
    """Reproduce MarlinFP8ScaledMMLinearKernel.process_weights_after_loading
    for a block-quant layer (size_k_first=False)."""
    from vllm.model_executor.layers.quantization.utils.fp8_utils import (
        process_fp8_weight_block_strategy,
    )
    from vllm.model_executor.layers.quantization.utils.marlin_utils_fp8 import (
        prepare_fp8_layer_for_marlin,
    )

    n, k = w_fp8.shape
    layer = torch.nn.Module()
    layer.weight = torch.nn.Parameter(w_fp8, requires_grad=False)
    layer.weight_scale_inv = torch.nn.Parameter(scales, requires_grad=False)
    layer.orig_dtype = torch.bfloat16
    layer.output_size_per_partition = n
    layer.input_size_per_partition = k
    layer.weight_block_size = [CFG_WEIGHT_BLOCK_SIZE, CFG_WEIGHT_BLOCK_SIZE]
    weight, weight_scale_inv = process_fp8_weight_block_strategy(
        layer.weight, layer.weight_scale_inv
    )
    layer.weight = torch.nn.Parameter(weight.data, requires_grad=False)
    layer.weight_scale_inv = torch.nn.Parameter(
        weight_scale_inv.data, requires_grad=False
    )
    prepare_fp8_layer_for_marlin(layer, size_k_first=False)
    return layer


def _import_gemv_triton():
    from vllm.v1.attention.ops.fp8_sm80 import _decode_fp8_f32, _decode_fp8_lut

    @triton.jit
    def _fp8_block_gemv_kernel(
        x_ptr,  # [M, K] bf16
        w_ptr,  # [N, K] fp8-e4m3 bytes
        scale_ptr,  # [N // QB, K // QB] fp32
        out_ptr,  # [M, N] bf16
        lut_ptr,
        stride_x_m,
        stride_w_n,
        stride_s_n,
        stride_o_m,
        K,
        N,
        QB: tl.constexpr,
        BLOCK_N: tl.constexpr,
        USE_LUT: tl.constexpr,
    ):
        # One CTA owns BLOCK_N output rows for one m: parallelism comes from N
        # (the anti-Marlin shape) and nothing is staged through smem -- at M=1
        # each weight byte is used exactly once, so staging cannot pay.
        pid_n = tl.program_id(0)
        m = tl.program_id(1)
        offs_n = pid_n * BLOCK_N + tl.arange(0, BLOCK_N)
        mask_n = offs_n < N
        offs_k = tl.arange(0, QB)
        acc = tl.zeros([BLOCK_N], dtype=tl.float32)
        for k0 in range(0, K, QB):
            x = tl.load(x_ptr + m * stride_x_m + k0 + offs_k).to(tl.float32)
            w_u8 = tl.load(
                w_ptr + offs_n[:, None] * stride_w_n + (k0 + offs_k)[None, :],
                mask=mask_n[:, None],
                other=0,
            )
            if USE_LUT:
                w = _decode_fp8_lut(w_u8, False, lut_ptr).to(tl.float32)
            else:
                w = _decode_fp8_f32(w_u8, False)
            # The K quant-block boundary aligns with the loop step, so each
            # iteration touches exactly one scale per output row.
            s = tl.load(
                scale_ptr + (offs_n // QB) * stride_s_n + k0 // QB,
                mask=mask_n,
                other=0.0,
            )
            acc += tl.sum(w * x[None, :], axis=1) * s
        tl.store(out_ptr + m * stride_o_m + offs_n, acc.to(tl.bfloat16), mask=mask_n)

    @triton.jit
    def _fp8_block_gemv_dot_kernel(
        x_ptr,  # [M, K] bf16, M <= 16
        w_ptr,  # [N, K] fp8-e4m3 bytes
        scale_ptr,  # [N // QB, K // QB] fp32
        out_ptr,  # [M, N] bf16
        stride_x_m,
        stride_w_n,
        stride_s_n,
        stride_o_m,
        M,
        K,
        N,
        QB: tl.constexpr,
        BLOCK_N: tl.constexpr,
    ):
        # v2: bit-shift fp8->fp16 decode (3 int ops/elem; exact incl. e4m3
        # denormals since every e4m3 value lands normal in fp16 after the 2^8
        # rebias, folded into the block scale) and tl.dot so the MAC rides the
        # idle tensor pipe. NaN weight bytes decode to finite garbage; block-
        # quantized checkpoints contain no NaN weights. M<=16 rides the MMA
        # padding for free, so one CTA covers the whole M<=8 dispatch range.
        pid_n = tl.program_id(0)
        offs_n = pid_n * BLOCK_N + tl.arange(0, BLOCK_N)
        mask_n = offs_n < N
        offs_m = tl.arange(0, 16)
        mask_m = offs_m < M
        offs_k = tl.arange(0, QB)
        acc = tl.zeros([16, BLOCK_N], dtype=tl.float32)
        for k0 in range(0, K, QB):
            x = tl.load(
                x_ptr + offs_m[:, None] * stride_x_m + (k0 + offs_k)[None, :],
                mask=mask_m[:, None],
                other=0.0,
            )
            u = tl.load(
                w_ptr + offs_n[:, None] * stride_w_n + (k0 + offs_k)[None, :],
                mask=mask_n[:, None],
                other=0,
            ).to(tl.uint16)
            w = (
                (((u & 0x80) << 8) | ((u & 0x7F) << 7))
                .to(tl.float16, bitcast=True)
                .to(tl.bfloat16)
            )
            s = tl.load(
                scale_ptr + (offs_n // QB) * stride_s_n + k0 // QB,
                mask=mask_n,
                other=0.0,
            )
            acc += tl.dot(x, tl.trans(w)) * (s * 256.0)[None, :]
        tl.store(
            out_ptr + offs_m[:, None] * stride_o_m + offs_n[None, :],
            acc.to(tl.bfloat16),
            mask=mask_m[:, None] & mask_n[None, :],
        )

    @triton.jit
    def _fp8_block_gemv_dot_split_kernel(
        x_ptr,  # [M, K] bf16, M <= 16
        w_ptr,  # [N, K] fp8-e4m3 bytes
        scale_ptr,  # [N // QB, K // QB] fp32
        part_ptr,  # [SPLIT_K, 16, N] fp32
        stride_x_m,
        stride_w_n,
        stride_s_n,
        stride_p_s,
        stride_p_m,
        M,
        K,
        N,
        QB: tl.constexpr,
        BLOCK_N: tl.constexpr,
        SPLIT_K: tl.constexpr,
    ):
        # Split-K flavour for the wide-K narrow-N shapes whose unsplit grid is
        # 16-48 CTAs: same decode/dot body, each split owns K/SPLIT_K, partials
        # reduced by _gemv_reduce_kernel (batch-1 grid starvation; split-K is
        # the in-tree existence proof that splitting a reduction fixes it).
        pid_n = tl.program_id(0)
        pid_s = tl.program_id(1)
        offs_n = pid_n * BLOCK_N + tl.arange(0, BLOCK_N)
        mask_n = offs_n < N
        offs_m = tl.arange(0, 16)
        mask_m = offs_m < M
        offs_k = tl.arange(0, QB)
        acc = tl.zeros([16, BLOCK_N], dtype=tl.float32)
        k_per_split = K // SPLIT_K
        k_lo = pid_s * k_per_split
        for k0 in range(k_lo, k_lo + k_per_split, QB):
            x = tl.load(
                x_ptr + offs_m[:, None] * stride_x_m + (k0 + offs_k)[None, :],
                mask=mask_m[:, None],
                other=0.0,
            )
            u = tl.load(
                w_ptr + offs_n[:, None] * stride_w_n + (k0 + offs_k)[None, :],
                mask=mask_n[:, None],
                other=0,
            ).to(tl.uint16)
            w = (
                (((u & 0x80) << 8) | ((u & 0x7F) << 7))
                .to(tl.float16, bitcast=True)
                .to(tl.bfloat16)
            )
            s = tl.load(
                scale_ptr + (offs_n // QB) * stride_s_n + k0 // QB,
                mask=mask_n,
                other=0.0,
            )
            acc += tl.dot(x, tl.trans(w)) * (s * 256.0)[None, :]
        tl.store(
            part_ptr
            + pid_s * stride_p_s
            + offs_m[:, None] * stride_p_m
            + offs_n[None, :],
            acc,
            mask=mask_m[:, None] & mask_n[None, :],
        )

    @triton.jit
    def _gemv_reduce_kernel(
        part_ptr,  # [SPLIT_K, 16, N] fp32
        out_ptr,  # [M, N] bf16
        stride_p_s,
        stride_p_m,
        stride_o_m,
        M,
        N,
        BLOCK_N: tl.constexpr,
        SPLIT_K: tl.constexpr,
    ):
        pid_n = tl.program_id(0)
        m = tl.program_id(1)
        offs_n = pid_n * BLOCK_N + tl.arange(0, BLOCK_N)
        mask_n = offs_n < N
        acc = tl.zeros([BLOCK_N], dtype=tl.float32)
        for s in tl.static_range(SPLIT_K):
            acc += tl.load(
                part_ptr + s * stride_p_s + m * stride_p_m + offs_n,
                mask=mask_n,
                other=0.0,
            )
        tl.store(out_ptr + m * stride_o_m + offs_n, acc.to(tl.bfloat16), mask=mask_n)

    return (
        _fp8_block_gemv_kernel,
        _fp8_block_gemv_dot_kernel,
        _fp8_block_gemv_dot_split_kernel,
        _gemv_reduce_kernel,
    )


def _launch_gemv(
    kernel,
    x: torch.Tensor,
    w_u8: torch.Tensor,
    scales: torch.Tensor,
    out: torch.Tensor,
    lut: torch.Tensor,
    block_n: int,
    num_warps: int,
    use_lut: bool,
) -> None:
    m, k = x.shape
    n = w_u8.shape[0]
    kernel[(triton.cdiv(n, block_n), m)](
        x,
        w_u8,
        scales,
        out,
        lut,
        x.stride(0),
        w_u8.stride(0),
        scales.stride(0),
        out.stride(0),
        k,
        n,
        QB=CFG_WEIGHT_BLOCK_SIZE,
        BLOCK_N=block_n,
        USE_LUT=use_lut,
        num_warps=num_warps,
    )


def _launch_gemv_dot(
    kernel,
    x: torch.Tensor,
    w_u8: torch.Tensor,
    scales: torch.Tensor,
    out: torch.Tensor,
    block_n: int,
    num_warps: int,
) -> None:
    m, k = x.shape
    n = w_u8.shape[0]
    kernel[(triton.cdiv(n, block_n),)](
        x,
        w_u8,
        scales,
        out,
        x.stride(0),
        w_u8.stride(0),
        scales.stride(0),
        out.stride(0),
        m,
        k,
        n,
        QB=CFG_WEIGHT_BLOCK_SIZE,
        BLOCK_N=block_n,
        num_warps=num_warps,
    )


def _launch_gemv_split(
    split_kernel,
    reduce_kernel,
    x: torch.Tensor,
    w_u8: torch.Tensor,
    scales: torch.Tensor,
    part: torch.Tensor,
    out: torch.Tensor,
    block_n: int,
    split_k: int,
) -> None:
    m, k = x.shape
    n = w_u8.shape[0]
    split_kernel[(triton.cdiv(n, block_n), split_k)](
        x,
        w_u8,
        scales,
        part,
        x.stride(0),
        w_u8.stride(0),
        scales.stride(0),
        part.stride(0),
        part.stride(1),
        m,
        k,
        n,
        QB=CFG_WEIGHT_BLOCK_SIZE,
        BLOCK_N=block_n,
        SPLIT_K=split_k,
        num_warps=4,
    )
    reduce_kernel[(triton.cdiv(n, 256), m)](
        part,
        out,
        part.stride(0),
        part.stride(1),
        out.stride(0),
        m,
        n,
        BLOCK_N=256,
        SPLIT_K=split_k,
        num_warps=4,
    )


def bench_dense_gemv(ms: list[int], block_ns: list[int], device: torch.device) -> None:
    from vllm.model_executor.layers.quantization.utils.marlin_utils_fp8 import (
        apply_fp8_marlin_linear,
    )
    from vllm.v1.attention.ops.fp8_sm80 import get_e4m3fn_bf16_lut

    kernel, dot_kernel, split_kernel, reduce_kernel = _import_gemv_triton()
    lut = get_e4m3fn_bf16_lut(device)
    rows = []
    # Best us per (arm, shape) for the per-step summary.
    step_us: dict[str, dict[str, float]] = {}
    for name, k, n, count in _DENSE_GEMM_SHAPES:
        w = torch.randn(n, k, dtype=torch.bfloat16, device=device) * 0.02
        w_fp8, scales = _fp8_block_quant(w)
        w_dq = _fp8_block_dequant(w_fp8, scales)
        marlin_layer = _make_marlin_layer(w_fp8.clone(), scales.clone(), device)
        w_u8 = w_fp8.view(torch.uint8)
        for m_tokens in ms:
            x = torch.randn(m_tokens, k, dtype=torch.bfloat16, device=device)
            out = torch.empty(m_tokens, n, dtype=torch.bfloat16, device=device)
            ref = (x.float() @ w_dq.float().t()).bfloat16()

            def run_marlin(x=x, layer=marlin_layer, n=n, k=k) -> torch.Tensor:
                return apply_fp8_marlin_linear(
                    x,
                    layer.weight,
                    layer.weight_scale_inv,
                    layer.workspace,
                    size_n=n,
                    size_k=k,
                    bias=None,
                )

            def run_cublas(x=x, w_dq=w_dq) -> torch.Tensor:
                return torch.nn.functional.linear(x, w_dq, None)

            variants: list[tuple[str, Callable[[], None], torch.Tensor | None]] = [
                ("marlin", run_marlin, run_marlin()),
                ("cublas-bf16", run_cublas, run_cublas()),
            ]
            # The Triton GEMV arms are M<=16 kernels by construction (the dot
            # tile and the split partial buffer are 16 rows); past that they
            # write garbage or fault, so only the library arms run.
            gemv_block_ns = block_ns if m_tokens <= 16 else []
            for block_n, use_lut in itertools.product(gemv_block_ns, (True, False)):
                label = f"gemv-{'lut' if use_lut else 'alu'}-bn{block_n}"
                fn = partial(
                    _launch_gemv, kernel, x, w_u8, scales, out, lut, block_n, 4, use_lut
                )
                fn()
                variants.append((label, fn, out.clone()))
            for block_n in gemv_block_ns:
                label = f"gemv-dot-bn{block_n}"
                fn = partial(
                    _launch_gemv_dot, dot_kernel, x, w_u8, scales, out, block_n, 4
                )
                fn()
                variants.append((label, fn, out.clone()))
            for block_n, split_k in itertools.product(gemv_block_ns, (2, 4, 8)):
                if k // split_k % CFG_WEIGHT_BLOCK_SIZE != 0:
                    continue
                part = torch.empty(split_k, 16, n, dtype=torch.float32, device=device)
                label = f"gemv-split{split_k}-bn{block_n}"
                fn = partial(
                    _launch_gemv_split,
                    split_kernel,
                    reduce_kernel,
                    x,
                    w_u8,
                    scales,
                    part,
                    out,
                    block_n,
                    split_k,
                )
                fn()
                variants.append((label, fn, out.clone()))

            weight_bytes = n * k  # fp8 payload; what an ideal GEMV must stream
            for label, fn, got in variants:
                err = (
                    float("nan")
                    if got is None
                    else (got.float() - ref.float()).abs().max().item()
                )
                us = _time_us(fn)
                gbs = float("nan") if us != us else weight_bytes / (us * 1e-6) / 1e9
                if m_tokens == 1 and us == us:
                    arm = label.split("-bn")[0]
                    if arm.startswith("gemv-split"):
                        arm = "gemv-split"
                    for key in (arm, "best-hybrid"):
                        best = step_us.setdefault(key, {})
                        prev = best.get(name)
                        best[name] = us if prev is None or us < prev else prev
                rows.append(
                    [
                        name,
                        str(m_tokens),
                        f"{k}x{n}",
                        label,
                        _fmt(us),
                        _fmt(gbs, ".0f"),
                        f"{err:.1e}",
                    ]
                )
    _print_table(
        "dense Marlin fp8 vs GEMV routes (per-rank TP=8 shapes)",
        ["layer", "M", "KxN", "impl", "us", "GB/s", "max|err|"],
        rows,
    )
    shape_counts = {name: count for name, _, _, count in _DENSE_GEMM_SHAPES}
    print(
        f"\nPer-step M=1 sum over {CFG_NUM_HIDDEN_LAYERS} layers "
        "(best config per arm; acceptance is beating marlin by >= 1.5 ms):"
    )
    for label, per_shape in sorted(step_us.items()):
        if set(per_shape) != set(shape_counts):
            print(f"  {label:>12}: incomplete ({sorted(per_shape)})")
            continue
        total_ms = (
            sum(per_shape[s] * shape_counts[s] for s in per_shape)
            * CFG_NUM_HIDDEN_LAYERS
            / 1e3
        )
        print(f"  {label:>12}: {total_ms:.2f} ms/step")


KERNELS = (
    "sparse-decode",
    "sparse-prefill",
    "bf16-gemv",
    "tail-launch",
    "prenorm-gemm",
    "mhc-pre",
    "dequant-gather",
    "indexer-logits",
    "dense-gemv",
)

# What a batch-1 decode step is made of, and where each part can be timed. This
# exists so that summing the sweeps above is never mistaken for a decomposition
# of the whole step: the covered rows are a minority of decode time, and a total
# that silently omits Marlin and MoE would understate the step by roughly half.
_DECODE_COVERAGE = [
    ("sparse-MLA decode", "~18%", "here: --kernel sparse-decode"),
    ("mHC pre big-fuse", "~6%", "here: --kernel mhc-pre"),
    ("dense Marlin fp8", "~26%", "here: --kernel dense-gemv (vs GEMV routes)"),
    ("MoE", "~10%", "benchmarks/kernels/benchmark_moe.py"),
    ("cuBLAS GEMV", "~13%", "not covered: plain torch matmul at M=1"),
    ("indexer MQA logits", "~11%", "here: --kernel indexer-logits (prefill path)"),
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
    parser.add_argument("--logits-ms", type=_int_list, default=[256, 2048])
    parser.add_argument(
        "--logits-ns",
        type=_int_list,
        default=[7168, 28672],
        help="compressed context lengths (= context/compress_ratio)",
    )
    parser.add_argument(
        "--maxnreg",
        type=_int_list,
        default=[0, 128],
        help="maxnreg values; 0 means unconstrained (today's 132 regs)",
    )
    parser.add_argument(
        "--logits-stages",
        type=_int_list,
        default=[2],
        help="num_stages values (production autotunes over 2 and 4)",
    )
    parser.add_argument(
        "--logits-groups",
        type=_int_list,
        default=[1, 4],
        help="KV_GROUP values: BLOCK_N tiles per CTA sharing one q-tile load",
    )
    parser.add_argument(
        "--decode-topk-len",
        type=int,
        default=TOPK_LEN,
        help="compressed top-k tokens per query (min(index_topk, ctx/ratio))",
    )
    parser.add_argument(
        "--decode-pool-rows",
        type=int,
        default=26875,
        help="rows the scattered top-k gather indexes into; keep this at the "
        "live ctx/compress_ratio (L2-resident), not the cache capacity",
    )
    parser.add_argument(
        "--prefill-ms",
        type=_int_list,
        default=[2048],
        help="chunk tokens; 2048 is the serving max_num_batched_tokens",
    )
    parser.add_argument(
        "--prefill-ctxs",
        type=_int_list,
        default=[8192, 32768],
        help="KV pool rows the top-k gather scatters across",
    )
    parser.add_argument(
        "--prefill-block-ks",
        type=_int_list,
        default=[16],
        help="BLOCK_K values; production picks 16 for head_dim >= 256",
    )
    parser.add_argument(
        "--prefill-stages",
        type=_int_list,
        default=[0],
        help="num_stages; 0 = omit the argument, which is what serving does",
    )
    parser.add_argument("--gemv-ms", type=_int_list, default=[1])
    parser.add_argument("--gemv-block-ns", type=_int_list, default=[16, 32, 64])
    parser.add_argument(
        "--gemv-block-ks", type=_int_list, default=[256, 512, 1024, 2048]
    )
    args = parser.parse_args()

    if args.coverage:
        print_decode_coverage()
        return

    torch.manual_seed(0)
    device = torch.device("cuda")
    selected = KERNELS if args.kernel == "all" else (args.kernel,)

    if "sparse-decode" in selected:
        bench_sparse_decode(
            args.batches,
            args.block_h,
            args.splits,
            args.warps,
            device,
            args.decode_topk_len,
            args.decode_pool_rows,
        )
    if "sparse-prefill" in selected:
        bench_sparse_prefill(
            args.prefill_ms,
            args.prefill_ctxs,
            args.block_h,
            args.prefill_block_ks,
            args.warps,
            args.maxnreg,
            args.prefill_stages,
            device,
        )
    if "prenorm-gemm" in selected:
        bench_prenorm_gemm(args.tokens, args.prenorm_configs, device)
    if "mhc-pre" in selected:
        bench_mhc_pre(args.tokens, args.sinkhorn_iters, device)
    if "dequant-gather" in selected:
        bench_dequant_gather(
            args.gather_lens, args.gather_reqs, args.gather_workers, device
        )
    if "indexer-logits" in selected:
        bench_indexer_logits(
            args.logits_ms,
            args.logits_ns,
            args.maxnreg,
            args.logits_stages,
            args.logits_groups,
            device,
        )
    if "tail-launch" in selected:
        bench_tail_launch(args.gemv_ms, device)
    if "bf16-gemv" in selected:
        bench_bf16_gemv(args.gemv_ms, device)
    if "dense-gemv" in selected:
        bench_dense_gemv(args.gemv_ms, args.gemv_block_ns, device)


if __name__ == "__main__":
    main()
