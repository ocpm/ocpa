from ocpa.algo.util.variants.versions import onephase, twophase
from ocpa.util.constants import ONE_PHASE, TWO_PHASE

VERSIONS = {TWO_PHASE: twophase.apply, ONE_PHASE: onephase.apply}


def apply(ocel, variant=TWO_PHASE, parameters=None):
    return VERSIONS[variant](ocel, parameters=parameters)
