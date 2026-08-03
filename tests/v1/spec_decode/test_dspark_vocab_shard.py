# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: Copyright contributors to the vLLM project
"""The sharded greedy selection must pick the same token as the replicated one.

Runs on CPU with no process group: the collective is simulated by splitting a
full-vocab logit row into shards and feeding the per-shard results to
``reduce_shard_argmax``, which is where the correctness actually lives.
"""

import pytest
import torch

from vllm.v1.worker.gpu.spec_decode.dspark.vocab_shard import reduce_shard_argmax

# DeepSeek-V4-Flash / Qwen3-DSpark draft vocab is 129,280; the small sizes
# exercise uneven splits, which is where an offset bug would hide.
VOCAB_SIZES = [129280, 4096, 1000, 17]
TP_SIZES = [2, 4, 8]


def _shard(logits: torch.Tensor, tp: int):
    """Split [B, V] into tp shards, returning per-shard max/argmax/offset."""
    v = logits.shape[-1]
    per = (v + tp - 1) // tp
    values, indices, starts = [], [], []
    for r in range(tp):
        lo, hi = r * per, min((r + 1) * per, v)
        if lo >= hi:
            # An empty trailing shard must never win; -inf is what a real rank
            # with no columns would contribute.
            values.append(torch.full((logits.shape[0],), float("-inf")))
            indices.append(torch.zeros(logits.shape[0], dtype=torch.long))
            starts.append(v)
            continue
        val, idx = logits[:, lo:hi].max(dim=-1)
        values.append(val)
        indices.append(idx)
        starts.append(lo)
    return (
        torch.stack(values),
        torch.stack(indices),
        torch.tensor(starts, dtype=torch.long),
    )


@pytest.mark.parametrize("vocab_size", VOCAB_SIZES)
@pytest.mark.parametrize("tp", TP_SIZES)
@pytest.mark.parametrize("batch", [1, 5])
def test_sharded_matches_replicated_argmax(vocab_size: int, tp: int, batch: int):
    torch.manual_seed(vocab_size * tp + batch)
    logits = torch.randn(batch, vocab_size, dtype=torch.float32)

    expected = logits.argmax(dim=-1)
    got = reduce_shard_argmax(*_shard(logits, tp))

    # Token-for-token equality, not closeness: this selects a token id.
    assert torch.equal(got, expected), (
        f"sharded selection diverged at V={vocab_size} tp={tp}: "
        f"{got.tolist()} vs {expected.tolist()}"
    )


@pytest.mark.parametrize("tp", TP_SIZES)
def test_ties_resolve_to_lowest_global_id(tp: int):
    """Exact ties are the one case torch.argmax leaves unspecified, so this
    module defines the rule and the test pins it."""
    vocab_size = 4096
    logits = torch.zeros(1, vocab_size, dtype=torch.float32)
    # Same maximum in several shards at once.
    per = vocab_size // tp
    tied = [r * per + 3 for r in range(tp)]
    for i in tied:
        logits[0, i] = 9.0

    got = reduce_shard_argmax(*_shard(logits, tp))
    assert got.item() == min(tied)


@pytest.mark.parametrize("tp", TP_SIZES)
def test_shard_order_does_not_matter(tp: int):
    """Ranks may deliver shards in any order; the reduction sorts by offset."""
    torch.manual_seed(0)
    logits = torch.randn(3, 4096, dtype=torch.float32)
    values, indices, starts = _shard(logits, tp)

    perm = torch.randperm(tp)
    shuffled = reduce_shard_argmax(values[perm], indices[perm], starts[perm])
    assert torch.equal(shuffled, logits.argmax(dim=-1))


def test_empty_trailing_shard_never_wins():
    """A rank holding no columns contributes -inf and must be ignored."""
    logits = torch.randn(2, 17, dtype=torch.float32)
    got = reduce_shard_argmax(*_shard(logits, 8))
    assert torch.equal(got, logits.argmax(dim=-1))
