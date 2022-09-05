from ocpa.algo.util.variants.versions import onephase
from ocpa.algo.util.variants.versions import twophase

TWO_PHASE= "two_phase"
ONE_PHASE = "one_phase"

VERSIONS = {TWO_PHASE: twophase.apply,
            ONE_PHASE: onephase.apply}


def apply(ocel, variant=TWO_PHASE, parameters=None):
    return VERSIONS[variant](ocel, parameters=parameters)
