# LMCache RAM + disk tiered KV offload (MP mode)

This fork can offload prefix KV to LMCache's multiprocess server, which keeps a
hot tier in pinned host RAM (L1) and a cold tier on local disk (L2). Only the
**MP connector** supports the hybrid KV cache groups used by DeepSeek-V4-Flash
and Qwen3.8-Flash-Next; the in-process `LMCacheConnectorV1` assumes a single
block size and geometry and must not be used with these models.

## Requirements

- LMCache built from the `fork-vllm-compat` branch (patch series in
  `/data/lmcache-notes/patches` on server5). Stock LMCache (as of 367196d7)
  cannot read this fork's unified KV cache layout: it looks for the removed
  `get_kv_cache_layout()`, treats `[B, H=1, N, C]` views as one slot per
  block, rejects block-outermost packing for non-MLA formats, ignores
  `tokens_per_state`, and would cache Qwen's per-request QSA ring buffer as
  positional KV.
- vLLM flags: `--enable-prefix-caching`; Mamba/GDN hybrids (Qwen3.8) also
  need `--mamba-cache-mode align` and `max-num-batched-tokens >= block size`.
- The LMCache chunk size must be a multiple of every KV group's block size.
  Qwen3.8-Flash-Next raises its attention block size to 784 so the Mamba
  page fits; DeepSeek-V4-Flash uses 256/64/8/4. Use `--chunk-size 784` and
  `256` respectively.

## Start the LMCache server

```bash
lmcache server --host 127.0.0.1 --port 5555 --http-port 18555 \
  --chunk-size 784 --separate-object-groups \
  --l1-size-gb 64 --eviction-policy LRU \
  --l2-adapter '{"type":"fs_native","base_path":"/kvcache/lmcache","num_workers":16,"max_capacity_gb":1000}'
```

- L1 is pinned host RAM sized by `--l1-size-gb`; LRU eviction starts at
  `--eviction-trigger-watermark` (default 0.9).
- Every stored chunk is pushed asynchronously to all `--l2-adapter`s
  (write-through). Lookups fall through L1 -> L2 and L2 hits are promoted
  back into L1. `max_capacity_gb` bounds the disk tier with LRU; `raw_block`
  (io_uring, checkpointed index) is the alternative for a dedicated NVMe.
- `POST /cache/clear` on the HTTP port drops L1 only (useful to test L2).

## Start vLLM

```bash
VLLM_PLE_CPU_OFFLOAD=1 vllm serve /data/Qwen38-Flash-Next-FP8 \
  --tensor-parallel-size 4 --enable-expert-parallel \
  --enable-prefix-caching --mamba-cache-mode align \
  --max-num-batched-tokens 2048 \
  --kv-transfer-config '{"kv_connector":"LMCacheMPConnector","kv_connector_module_path":"lmcache.integration.vllm.lmcache_mp_connector","kv_role":"kv_both","kv_connector_extra_config":{"lmcache.mp.host":"127.0.0.1","lmcache.mp.port":5555}}'
```

`kv_connector_module_path` selects LMCache's own connector instead of the
older copy vendored in `vllm/distributed/kv_transfer`. `--kv-offloading-backend
lmcache` maps to the vendored copy and does not carry the module path.

## Status (2026-08-27, 4x A6000, server5)

| model | groups registered | transfer mechanics | output equivalence (temperature 0, 220-token generations) |
|---|---|---|---|
| Qwen3.8-Flash-Next-FP8 | 6 kernel groups (QSA main bs=784, compressed keys bs=196, 3 GDN + 1 PLE recurrent, ring buffer excluded) | store -> APC reset -> L1 hit and L1 eviction -> L2 hit (12 keys / 18 ms) both work | 3-chunk hits and the L2 2-chunk hit were bit-identical; 5- and 8-chunk hits diverged (prefix 18/986 and 802/931 chars) in both `align` and `all` Mamba cache modes |
| DeepSeek-V4-Flash | 8 kernel groups (indexer 132 B rows, C4A/C128A 584 B rows, SWA, fp32 compressor states) | 15 chunks / 3840 tokens hit from L1 and from L2 (42 ms) | not assessable: `master` DSv4 output is wrong on SM86 even without LMCache |

Open issues:

- **Recurrent-state correctness.** vLLM's `align` Mamba mode keeps only the
  latest boundary snapshot; earlier chunks report the null block (id 0), so
  LMCache stores null pages (`[5, 0, 0]` at store, `[0, 0, 4]` at retrieve
  in the connector debug log). A hit whose tail chunk carries a null page
  resumes from a wrong state. `--mamba-cache-mode all` did not fix the
  divergence either, so the stored/retrieved recurrent pages need the
  "tail-only" handling LMCache's hybrid design doc defers. Until then treat
  LMCache hits on Qwen3.8 as **not bit-exact**; use the fork's native
  `TieringOffloadingSpec` for production.
- Store coverage is capped by the recurrent groups' allocated block count
  (`min` over positional groups); 2-chunk prefixes also failed to look up
  right after being stored. Both need the same recurrent-group semantics.
- `POST /cache/clear` (L1) leaves the server unable to find anything stored
  afterwards; do not use it in tests.
- DeepSeek-V4-Flash on `master` is broken on SM86 with or without LMCache:
  three crashes from the 915f59b6a1 port were fixed (9cc0fd80a0, 68b5981ee9,
  ebf17a7aa5) but decode still produces garbage. Keep DSv4 deployments on the
  v0.6.x images.
