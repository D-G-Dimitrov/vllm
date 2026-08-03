# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: Copyright contributors to the vLLM project
"""Vocab-sharded greedy selection for the DSpark Markov head.

``DSparkMarkovHead.markov_w2`` is replicated by design (``disable_tp=True``):
the head runs once per draft position, and its docstring argues that sharding
it "would add an all-reduce and a full-vocab gather to each position". That is
true of the *probabilistic* path, which needs whole processed logit rows to
verify against. It is not true of the greedy path, where the only thing read
off the vocab axis is an argmax -- and an argmax reduces.

So each rank can own ``V/TP`` columns, take a shard-local max, and exchange
one ``(value, index)`` pair per rank: 8 pairs = 64 bytes, against a
[B, 129280] gather. The GEMM and the argmax both shrink by the TP factor.

**Tie-breaking is the correctness crux, not seeding.** The greedy path has no
Gumbel noise (see ``_sample_sequential``: the ``draft_logits is None`` branch
is a bare ``logits_i.argmax``), so every rank computes exact logits for its own
columns and there is no cross-rank randomness to synchronise. What does need
pinning down is what happens when two vocab entries hold the same maximum:
this module always resolves to the **lowest global vocab id**, which it gets
by breaking rank ties toward the lowest rank. ``torch.argmax`` does not
document its own tie-break, so an exact float tie is the one input on which
sharded and replicated selection may legitimately disagree; with distinct
logits -- the case for any real draft head -- they agree exactly.
"""

import torch


def reduce_shard_argmax(
    shard_values: torch.Tensor,
    shard_indices: torch.Tensor,
    vocab_starts: torch.Tensor,
) -> torch.Tensor:
    """Combine per-shard argmax results into global vocab ids.

    Pure and device-agnostic so it can be tested without a process group.

    Args:
        shard_values: ``[num_shards, B]`` shard-local maximum logit.
        shard_indices: ``[num_shards, B]`` shard-local argmax, shard-relative.
        vocab_starts: ``[num_shards]`` first global vocab id of each shard.

    Returns:
        ``[B]`` global vocab ids, ties resolved to the lowest global id.
    """
    global_ids = shard_indices + vocab_starts.view(-1, 1).to(shard_indices.dtype)
    # torch.max over dim 0 returns the first maximal row, so ordering shards by
    # ascending vocab_start already breaks ties toward the lowest global id --
    # but only if the caller passes them in that order, which is not something
    # to leave implicit.
    order = torch.argsort(vocab_starts)
    values = shard_values[order]
    ids = global_ids[order]
    best = values.argmax(dim=0)
    return ids.gather(0, best.unsqueeze(0)).squeeze(0)


def sharded_greedy_select(
    shard_logits: torch.Tensor,
    vocab_start: int,
    tp_group,
) -> torch.Tensor:
    """Greedy argmax over a vocab-sharded logit row.

    ``shard_logits`` is ``[B, V/TP]``, this rank's columns only. Exchanges
    ``2 x B`` floats per rank instead of gathering the whole vocab.
    """
    local_value, local_index = shard_logits.max(dim=-1)
    # One tensor so the exchange is a single collective: row 0 values, row 1
    # indices carried as float (vocab ids are far below 2**24, so the round
    # trip is exact).
    packed = torch.stack([local_value.float(), local_index.to(torch.float32)], dim=0)
    gathered = tp_group.all_gather(packed.unsqueeze(0), dim=0)
    values = gathered[:, 0]
    indices = gathered[:, 1].to(torch.long)
    starts = torch.as_tensor(
        _vocab_starts(vocab_start, tp_group),
        device=shard_logits.device,
        dtype=torch.long,
    )
    return reduce_shard_argmax(values, indices, starts)


def _vocab_starts(vocab_start: int, tp_group) -> list[int]:
    """Every rank's first global vocab id, in rank order."""
    starts = [0] * tp_group.world_size
    starts[tp_group.rank_in_group] = vocab_start
    gathered = tp_group.all_gather(torch.tensor(starts, dtype=torch.long, device="cpu"))
    return gathered.tolist()
