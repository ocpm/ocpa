from ocpa.algo.util.variants.versions import onephase
from ocpa.algo.util.variants.versions import twophase
<<<<<<< HEAD

TWO_PHASE = "two_phase"
ONE_PHASE = "one_phase"
=======
from ocpa.util.constants import TWO_PHASE, ONE_PHASE
>>>>>>> upstream/main

VERSIONS = {TWO_PHASE: twophase.apply, ONE_PHASE: onephase.apply}


def apply(ocel, variant=TWO_PHASE, parameters=None):
    return VERSIONS[variant](ocel, parameters=parameters)
