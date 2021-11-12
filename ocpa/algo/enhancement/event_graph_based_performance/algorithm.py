from ocpa.algo.enhancement.event_graph_based_performance.versions import perfectly_fitting

PERFECTLY_FITTING = "perfectly_fitting"

VERSIONS = {PERFECTLY_FITTING: perfectly_fitting.apply}


def apply(ocpn, cegs, variant=PERFECTLY_FITTING, parameters=None):
    return VERSIONS[variant](ocpn, cegs, parameters=parameters)
