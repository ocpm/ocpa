from ocpa.objects.log.converter.versions import jsonocel_to_mdl

JSONOCEL_TO_MDL = "json_to_mdl"

VERSIONS = {JSONOCEL_TO_MDL: jsonocel_to_mdl.apply}


def apply(ocel, variant=JSONOCEL_TO_MDL, parameters=None):
    return VERSIONS[variant](ocel, parameters=parameters)
