import inspect

import vllm

print("VLLM_FILE:", vllm.__file__, flush=True)

import vllm.model_executor.layers.quantization.inc.inc as incmod

print("INC_FILE:", incmod.__file__, flush=True)
src = inspect.getsource(incmod.INCConfig.get_quant_method)
print("MARKER_return_None:", "return None" in src, flush=True)
print("MARKER_mtp_prefix_used:", "_mtp_checkpoint_prefix(prefix" in src, flush=True)

from vllm.model_executor.layers.linear import LinearBase, UnquantizedLinearMethod


class DummyLinear(LinearBase):
    """Minimal concrete LinearBase: what the rule must still unquantize."""

    def __init__(self):
        super().__init__(input_size=8, output_size=8, bias=False)

    def forward(self, x):  # pragma: no cover
        return x


class NotALayer:
    """Anything that is neither LinearBase, ParallelLMHead, nor RoutedExperts."""


def make_cfg():
    cfg = incmod.INCConfig.__new__(incmod.INCConfig)
    cfg.extra_config = {"model.layers.0.mlp.gate": {"bits": 16}}
    cfg.block_name_to_quantize = None
    cfg.config_parser = None
    return cfg


def probe(label, layer):
    cfg = make_cfg()
    try:
        got = cfg.get_quant_method(layer, prefix="model.layers.0.mlp.gate")
        out = type(got).__name__
    except Exception as exc:  # noqa: BLE001
        out = "RAISED:%s:%s" % (type(exc).__name__, exc)
    print("RESULT %-14s -> %s" % (label, out), flush=True)


probe("linear", DummyLinear())
probe("not_a_layer", NotALayer())
try:
    from vllm.model_executor.layers.vocab_parallel_embedding import ParallelLMHead

    probe("lm_head", ParallelLMHead(128, 16, padding_size=16))
except Exception as exc:  # noqa: BLE001
    print("RESULT lm_head       -> SKIPPED_BUILD:%s:%s" % (type(exc).__name__, exc), flush=True)
print("PROBE_DONE", flush=True)
