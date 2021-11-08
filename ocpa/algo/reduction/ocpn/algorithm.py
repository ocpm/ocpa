from ocpa.algo.reduction.ocpn.versions import murata

MURATA = "murata"

VERSIONS = {MURATA: murata.apply}


def apply(df, variant=MURATA, parameters=None):
    return VERSIONS[variant](df, parameters=parameters)
