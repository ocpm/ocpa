from ocpa.algo.discovery.ocpn.versions import inductive_and_tr

INDUCTIVE_AND_TR = "inductive_and_tr"

VERSIONS = {INDUCTIVE_AND_TR: inductive_and_tr.apply}


def apply(ocel, variant=INDUCTIVE_AND_TR, parameters=None):
    return VERSIONS[variant](ocel.log, parameters=parameters)
