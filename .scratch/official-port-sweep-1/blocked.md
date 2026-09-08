# Blocked — awaiting owner decision

| item | sha | conflict | recommended resolution |
|---|---|---|---|
| 123 | f5c3cc240b | `sparse_attn_indexer.py`: fork re-keyed `num_rows`->`num_padded_tokens` (TP-shard consistency, +231/-19 wtdcode region); upstream bumps 32->64 on the same line | `and num_padded_tokens <= 64` (safe: `num_rows <= num_padded_tokens` proven; kernel re-checks `num_rows <= 64`; SM87 never reaches this path) |

Full analysis: `outcomes.log.md` section "123." Tree left clean at `2cc1a12bc` (cherry-pick aborted).
