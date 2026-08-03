# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: Copyright contributors to the vLLM project
"""`fuse_input_gemm_weights` merges the three bf16 attention input GEMMs.

The method is exercised unbound against a stub carrying only the attributes it
reads, so the test needs no model, no config and no weights on disk. What it
has to pin is that the merge is a re-layout and not a copy: after fusing, each
module's weight must be the same values it had, backed by the concatenated
buffer, because `attn_gemm_parallel_execute` splits that buffer's output by
those same row counts and the un-fused fallback still reads the module weights.
"""

import pytest
import torch
from torch import nn

from vllm.models.deepseek_v4.attention import DeepseekV4Attention
from vllm.platforms import current_platform

pytestmark = pytest.mark.skipif(
    not current_platform.is_cuda(),
    reason="the fusion is gated to CUDA (XPU's indexer op wants bf16 weights)",
)

HIDDEN = 256
# Row counts in the checkpoint's proportion (compressor, indexer compressor,
# weights_proj), scaled down.
N_COMP, N_IDX, N_WP = 128, 32, 8


def _linear(n: int, device: str) -> nn.Module:
    mod = nn.Module()
    mod.weight = nn.Parameter(
        torch.randn(n, HIDDEN, dtype=torch.bfloat16, device=device),
        requires_grad=False,
    )
    return mod


def _stub(device: str = "cuda"):
    compressor = nn.Module()
    compressor.fused_wkv_wgate = _linear(N_COMP, device)
    indexer = nn.Module()
    indexer.compressor = nn.Module()
    indexer.compressor.fused_wkv_wgate = _linear(N_IDX, device)
    indexer.weights_proj = _linear(N_WP, device)

    stub = nn.Module()
    stub.compressor = compressor
    stub.indexer = indexer
    stub.hidden_size = HIDDEN
    stub.fused_input_weight = None
    stub.fused_input_splits = []
    return stub


def test_fuse_input_gemm_weights_preserves_values_and_layout():
    stub = _stub()
    originals = [
        stub.compressor.fused_wkv_wgate.weight.clone(),
        stub.indexer.compressor.fused_wkv_wgate.weight.clone(),
        stub.indexer.weights_proj.weight.clone(),
    ]

    DeepseekV4Attention.fuse_input_gemm_weights(stub)

    assert stub.fused_input_splits == [N_COMP, N_IDX, N_WP]
    merged = stub.fused_input_weight
    assert merged.shape == (N_COMP + N_IDX + N_WP, HIDDEN)
    assert merged.is_contiguous()

    weights = [
        stub.compressor.fused_wkv_wgate.weight,
        stub.indexer.compressor.fused_wkv_wgate.weight,
        stub.indexer.weights_proj.weight,
    ]
    for original, weight in zip(originals, weights):
        assert torch.equal(weight, original)
        # A row-slice of a contiguous [N, K] tensor is contiguous, which is
        # what lets the modules keep using their weights unchanged.
        assert weight.is_contiguous()
        assert weight.data_ptr() >= merged.data_ptr()
        assert (
            weight.untyped_storage().data_ptr() == merged.untyped_storage().data_ptr()
        )

    # Splitting the merged GEMM's output must reproduce the separate GEMMs.
    x = torch.randn(3, HIDDEN, dtype=torch.bfloat16, device=merged.device)
    fused_out = torch.mm(x, merged.T, out_dtype=torch.float32).split(
        stub.fused_input_splits, dim=-1
    )
    for original, part in zip(originals, fused_out):
        reference = torch.mm(x, original.T, out_dtype=torch.float32)
        torch.testing.assert_close(part, reference, rtol=1e-5, atol=1e-5)


def test_fuse_input_gemm_weights_skips_layers_without_an_indexer():
    stub = _stub()
    stub.indexer = None
    DeepseekV4Attention.fuse_input_gemm_weights(stub)
    assert stub.fused_input_weight is None

    stub = _stub()
    stub.compressor = None
    DeepseekV4Attention.fuse_input_gemm_weights(stub)
    assert stub.fused_input_weight is None
