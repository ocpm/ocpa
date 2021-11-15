from ocpa.algo.discovery.ocpn.versions import inductive_and_tr
from ocpa.objects.log.obj import OCEL

INDUCTIVE_AND_TR = "inductive_and_tr"

VERSIONS = {INDUCTIVE_AND_TR: inductive_and_tr.apply}


def apply(ocel, variant=INDUCTIVE_AND_TR, parameters=None):
    if type(ocel) == OCEL:
        return VERSIONS[variant](ocel.log, parameters=parameters)
    else:
        return VERSIONS[variant](ocel, parameters=parameters)
