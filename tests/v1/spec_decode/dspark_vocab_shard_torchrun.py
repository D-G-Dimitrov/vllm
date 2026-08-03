# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: Copyright contributors to the vLLM project
"""8-rank check of DSpark's vocab-sharded greedy drafting.

Not named ``test_*`` on purpose: it needs a real TP process group, so it is
launched by ``test_dspark_vocab_shard.py`` as

    torchrun --nproc_per_node=8 tests/v1/spec_decode/dspark_vocab_shard_torchrun.py

What it covers that a single-process test cannot: the shipped entry point.
``DSparkSpeculator._sample_sequential`` is driven directly -- the real
function, on real ``ParallelLMHead``\\ s whose weights went through the real
vocab-parallel ``weight_loader`` -- once with the local-argmax reduction off
and once with it on, and the two drafts must agree token for token. The
previous iteration of this feature had 31 green unit tests over the reduction
while the shipped path could not run at all, which is the hole this closes.
"""

import os
import sys
from types import SimpleNamespace

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))

import torch  # noqa: E402
import torch.distributed as dist  # noqa: E402
import torch.nn as nn  # noqa: E402

from vllm.config import VllmConfig, set_current_vllm_config  # noqa: E402
from vllm.distributed.parallel_state import (  # noqa: E402
    ensure_model_parallel_initialized,
    init_distributed_environment,
)
from vllm.model_executor.layers.logits_processor import LogitsProcessor  # noqa: E402
from vllm.model_executor.layers.vocab_parallel_embedding import (  # noqa: E402
    ParallelLMHead,
)
from vllm.model_executor.models.qwen3_dspark import (  # noqa: E402
    DSparkMarkovHead,
    Qwen3DSparkForCausalLM,
)
from vllm.v1.worker.gpu.spec_decode.dspark.speculator import (  # noqa: E402
    DSparkSpeculator,
)

# Checkpoint constants (DeepSeek-V4-Flash-0731 config.json): full-vocab draft,
# markov_rank 256, dspark_block_size 5. hidden_size is cut to 512 -- it only
# sets the base GEMM's K, and nothing here depends on its value.
VOCAB = 129280
MARKOV_RANK = 256
HIDDEN = 512
N_SPEC = 5
BATCH = 4


class _StubDSpark(nn.Module):
    """A DSpark draft model reduced to its head, borrowing the shipped methods.

    The class attributes are the real function objects from
    ``Qwen3DSparkForCausalLM``, so this exercises the shipped code rather than
    a copy of it; only the backbone (which produces ``head_hidden``) is stubbed
    out, and the speculator is handed that hidden state directly.
    """

    compute_draft_logits = Qwen3DSparkForCausalLM.compute_draft_logits
    compute_draft_logits_shard = Qwen3DSparkForCausalLM.compute_draft_logits_shard
    select_draft_token_shard = Qwen3DSparkForCausalLM.select_draft_token_shard
    markov_embed = Qwen3DSparkForCausalLM.markov_embed
    markov_bias = Qwen3DSparkForCausalLM.markov_bias
    map_draft_to_target = Qwen3DSparkForCausalLM.map_draft_to_target

    draft_id_to_target_id = None

    def __init__(self, lm_head, dtype: torch.dtype, shard_vocab: bool) -> None:
        super().__init__()
        self.lm_head = lm_head
        self.logits_processor = LogitsProcessor(VOCAB)
        self.model = nn.Module()
        self.model.markov_head = DSparkMarkovHead(
            VOCAB,
            VOCAB,
            MARKOV_RANK,
            prefix="markov_head",
            shard_vocab=shard_vocab,
        )
        self.model.markov_head.to(dtype=dtype, device="cuda")


def _make_speculator(model, use_shard: bool, num_reqs: int):
    """A DSparkSpeculator carrying only what _sample_sequential reads."""
    spec = DSparkSpeculator.__new__(DSparkSpeculator)
    spec.model = model
    spec.num_speculative_steps = N_SPEC
    spec.use_local_argmax_reduction = use_shard
    spec.draft_logits = None
    spec.sample_indices = torch.arange(
        num_reqs * N_SPEC, dtype=torch.int64, device="cuda"
    )
    spec.sample_idx_mapping = torch.zeros(
        num_reqs * N_SPEC, dtype=torch.int32, device="cuda"
    )
    spec.sample_pos = torch.arange(num_reqs * N_SPEC, dtype=torch.int64, device="cuda")
    spec._anchor_idx = torch.arange(num_reqs, dtype=torch.int64, device="cuda") * N_SPEC
    spec.input_buffers = SimpleNamespace(
        input_ids=torch.randint(
            0, VOCAB, (num_reqs * N_SPEC,), dtype=torch.int64, device="cuda"
        )
    )
    spec.draft_tokens = torch.zeros(num_reqs, N_SPEC, dtype=torch.int64, device="cuda")
    return spec


def _run(dtype: torch.dtype, rank: int) -> bool:
    torch.manual_seed(0)  # identical draw on every rank
    lm_head = ParallelLMHead(VOCAB, HIDDEN, bias=False, params_dtype=dtype).cuda()
    # Both arms share the base head (it is vocab-parallel either way) and load
    # the same full markov_w2 through each layout's own weight_loader.
    full_lm = torch.randn(VOCAB, HIDDEN, dtype=torch.float32).to(dtype)
    full_w2 = torch.randn(VOCAB, MARKOV_RANK, dtype=torch.float32).to(dtype)
    lm_head.weight_loader(lm_head.weight, full_lm)

    arms = {}
    for use_shard in (False, True):
        model = _StubDSpark(lm_head, dtype, shard_vocab=use_shard)
        w2 = model.model.markov_head.markov_w2
        w2.weight_loader(w2.weight, full_w2)
        model.model.markov_head.markov_w1.weight.data.normal_(0, 0.02)
        arms[use_shard] = model

    expected_width = VOCAB // dist.get_world_size()
    got_width = arms[True].model.markov_head.markov_w2.weight.shape[0]
    assert got_width == expected_width, f"{got_width} != {expected_width}"
    assert arms[False].model.markov_head.markov_w2.weight.shape[0] == VOCAB

    head_hidden = torch.randn(BATCH * N_SPEC, HIDDEN, device="cuda").to(dtype)
    # markov_w1 must match across arms so `prev` feeds the same embedding.
    arms[True].model.markov_head.markov_w1.weight.data.copy_(
        arms[False].model.markov_head.markov_w1.weight.data
    )

    # Trap #8 guard: a green arm that ran the other path is worse than a red
    # one. Each arm's unused entry point is poisoned, so a silent fallback --
    # in either direction -- fails loudly instead of agreeing trivially.
    def _poison(name):
        def fail(*args, **kwargs):
            raise AssertionError(f"{name} must not run on this arm")

        return fail

    arms[True].markov_bias = _poison("markov_bias")
    arms[True].compute_draft_logits = _poison("compute_draft_logits")
    arms[False].select_draft_token_shard = _poison("select_draft_token_shard")
    arms[False].compute_draft_logits_shard = _poison("compute_draft_logits_shard")

    drafts = {}
    for use_shard in (False, True):
        spec = _make_speculator(arms[use_shard], use_shard, BATCH)
        # Same anchor tokens on both arms and on every rank.
        spec.input_buffers.input_ids.copy_(
            torch.arange(BATCH * N_SPEC, dtype=torch.int64, device="cuda") * 977 % VOCAB
        )
        spec._sample_sequential(BATCH, head_hidden)
        drafts[use_shard] = spec.draft_tokens.clone()

    ok = torch.equal(drafts[False], drafts[True])
    # The reduction has to be reaching across ranks: if every selected id came
    # from one shard, agreement would say nothing about the exchange.
    owners = (drafts[True] // expected_width).unique()
    if owners.numel() < 2:
        ok = False
        if rank == 0:
            print(f"  degenerate: all draft ids from shard(s) {owners.tolist()}")
    if rank == 0:
        tag = str(dtype).replace("torch.", "")
        print(f"[{tag}] replicated == sharded draft tokens: {ok}")
        if not ok:
            diff = (drafts[False] != drafts[True]).nonzero()
            print(f"  replicated {drafts[False].tolist()}")
            print(f"  sharded    {drafts[True].tolist()}")
            print(f"  mismatched at {diff.tolist()}")
    return ok


def _capture(rank: int) -> bool:
    """The draft step is captured under a FULL cudagraph, so the sharded
    selection -- which contains a collective -- has to be capturable."""
    torch.manual_seed(0)
    lm_head = ParallelLMHead(
        VOCAB, HIDDEN, bias=False, params_dtype=torch.bfloat16
    ).cuda()
    # Load it: ParallelLMHead allocates with torch.empty, and uninitialized
    # bytes decode as NaN often enough that an unloaded head turns this into a
    # NaN-robustness test by accident (which is how the sentinel bug in
    # reduce_global_argmax was found -- it now has its own test).
    lm_head.weight_loader(
        lm_head.weight, torch.randn(VOCAB, HIDDEN, dtype=torch.float32).bfloat16()
    )
    model = _StubDSpark(lm_head, torch.bfloat16, shard_vocab=True)
    w2 = model.model.markov_head.markov_w2
    w2.weight_loader(
        w2.weight, torch.randn(VOCAB, MARKOV_RANK, dtype=torch.float32).bfloat16()
    )
    spec = _make_speculator(model, True, BATCH)
    head_hidden = torch.randn(
        BATCH * N_SPEC, HIDDEN, device="cuda", dtype=torch.bfloat16
    )
    try:
        s = torch.cuda.Stream()
        s.wait_stream(torch.cuda.current_stream())
        with torch.cuda.stream(s):
            spec._sample_sequential(BATCH, head_hidden)
        torch.cuda.current_stream().wait_stream(s)
        eager = spec.draft_tokens.clone()

        g = torch.cuda.CUDAGraph()
        with torch.cuda.graph(g):
            spec._sample_sequential(BATCH, head_hidden)
        spec.draft_tokens.zero_()
        g.replay()
        torch.accelerator.synchronize()
        ok = torch.equal(eager, spec.draft_tokens)
        if rank == 0:
            print(f"[capture] captured replay == eager: {ok}")
        return ok
    except Exception as exc:  # noqa: BLE001
        if rank == 0:
            print(f"[capture] FAILED: {type(exc).__name__}: {exc}")
        return False


def main() -> None:
    rank = int(os.environ["RANK"])
    world = int(os.environ["WORLD_SIZE"])
    torch.accelerator.set_device_index(rank)
    # Held in a variable: inlining lets the context manager be collected and
    # every rank then dies on "Current vLLM config is not set".
    ctx = set_current_vllm_config(VllmConfig())
    ctx.__enter__()
    init_distributed_environment(
        world_size=world, rank=rank, local_rank=rank, backend="nccl"
    )
    ensure_model_parallel_initialized(world, 1)

    results = [
        _run(torch.float32, rank),
        _run(torch.bfloat16, rank),
        _capture(rank),
    ]
    dist.barrier()
    if rank == 0:
        print("RESULT", "PASS" if all(results) else "FAIL")
    dist.destroy_process_group()
    sys.exit(0 if all(results) else 1)


if __name__ == "__main__":
    main()
