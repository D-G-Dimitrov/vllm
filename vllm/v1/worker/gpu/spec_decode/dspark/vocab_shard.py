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
    return reduce_global_argmax(shard_values, global_ids)


def reduce_global_argmax(
    shard_values: torch.Tensor,
    global_ids: torch.Tensor,
) -> torch.Tensor:
    """Reduce per-shard maxima that already carry global vocab ids.

    Separate from :func:`reduce_shard_argmax` because the wire format matters:
    converting shard-local indices to global ones *before* the exchange is what
    lets the collective carry (value, id) pairs and nothing else. The
    alternative -- gathering local indices and reconstructing ids afterwards --
    needs every rank's vocab_start, i.e. a second collective, which is where
    the first version of this module went wrong.

    Ties resolve to the lowest global id by taking the minimum id among the
    rows that achieve the maximum, so the result does not depend on row order
    (``torch.argmax`` picking the first maximal row would, and argsort is not
    documented stable).
    """
    best_value = shard_values.max(dim=0, keepdim=True).values
    unreachable = torch.iinfo(global_ids.dtype).max
    candidates = torch.where(
        shard_values == best_value, global_ids, torch.full_like(global_ids, unreachable)
    )
    return candidates.min(dim=0).values


def sharded_greedy_select(
    shard_logits: torch.Tensor,
    vocab_start: int,
    tp_group,
) -> torch.Tensor:
    """Greedy argmax over a vocab-sharded logit row.

    ``shard_logits`` is ``[B, V/TP]``, this rank's columns only, and
    ``vocab_start`` is this rank's first global vocab id (for a
    ``VocabParallelEmbedding`` head that is
    ``lm_head.shard_indices.org_vocab_start_index``). Exchanges ``2 x B``
    floats per rank instead of gathering the whole vocab.

    Exactly one collective, on GPU tensors only. The first version of this
    function ran a second all_gather to learn every rank's ``vocab_start`` --
    on a CPU tensor, which vLLM's ``all_gather`` cannot dispatch at all
    (`NotImplementedError: ... with arguments from the 'CPU' backend`), so it
    could not run on a real process group and would have been a host sync
    inside the captured draft step even if it had. Converting local ids to
    global ones before the exchange removes the need for it, which is also
    what the in-tree `LogitsProcessor.get_top_tokens` does.
    """
    local_value, local_index = shard_logits.max(dim=-1)
    global_index = local_index + vocab_start
    # One tensor so the exchange is a single collective: row 0 values, row 1
    # ids carried as float (vocab ids are far below 2**24, so the round trip
    # is exact).
    packed = torch.stack([local_value.float(), global_index.to(torch.float32)], dim=0)
    gathered = tp_group.all_gather(packed.unsqueeze(0), dim=0)
    return reduce_global_argmax(gathered[:, 0], gathered[:, 1].to(torch.long))
