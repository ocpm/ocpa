from ocpa.algo.enhancement.ocpn_analysis.reduction.versions import murata

MURATA = "murata"

VERSIONS = {MURATA: murata.apply}


def apply(ocpn, variant=MURATA, parameters=None):
    return VERSIONS[variant](ocpn, parameters=parameters)
