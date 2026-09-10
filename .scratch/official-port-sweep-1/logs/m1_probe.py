import inspect

import vllm

print("TREE_VLLM_FILE:", vllm.__file__, flush=True)

from vllm.v1.kv_offload.tiering.manager import TieringOffloadingManager

src = inspect.getsource(TieringOffloadingManager.shutdown)
print("MARKER_shutdown_error_count:", src.count("shutdown_error"), flush=True)
print("MARKER_tier_attempts_all:", "for tier_idx, tier in enumerate" in src, flush=True)


class StubTier:
    tier_type = "stub"

    def __init__(self, i, boom=False):
        self.i, self.boom, self.called = i, boom, False

    def shutdown(self):
        self.called = True
        if self.boom:
            raise RuntimeError("boom-%d" % self.i)


class StubPrimary:
    def __init__(self):
        self.called = False

    def shutdown(self):
        self.called = True


def run(boom_indices):
    m = TieringOffloadingManager.__new__(TieringOffloadingManager)
    tiers = [StubTier(i, boom=(i in boom_indices)) for i in (1, 2)]
    p = StubPrimary()
    m.secondary_tiers = tiers
    m.primary_tier = p
    err = None
    try:
        m.shutdown()
    except Exception as exc:  # noqa: BLE001
        err = exc
    return (
        "tier1_called=%s tier2_called=%s primary_called=%s err=%s"
        % (tiers[0].called, tiers[1].called, p.called, err)
    )


# scenario 1: happy path -- both tiers then primary, no error (must be IDENTICAL both arms)
print("SCENARIO_happy :", run([]), flush=True)
# scenario 2: first secondary tier raises -- THIS is the discriminator
print("SCENARIO_fail1 :", run([1]), flush=True)
# scenario 3: both raise -- which error survives
print("SCENARIO_fail12:", run([1, 2]), flush=True)
print("PROBE_DONE", flush=True)
