from ocpa.objects.log.converter.versions import jsonocel_to_mdl
<<<<<<< HEAD

JSONOCEL_TO_MDL = "json_to_mdl"

VERSIONS = {JSONOCEL_TO_MDL: jsonocel_to_mdl.apply}
=======
from ocpa.objects.log.converter.versions import mdl_to_ocel

JSONOCEL_TO_MDL = "json_to_mdl"
MDL_TO_OCEL = "mdl_to_ocel"

VERSIONS = {JSONOCEL_TO_MDL: jsonocel_to_mdl.apply,
            MDL_TO_OCEL: mdl_to_ocel.apply}
>>>>>>> origin/Publishing


def apply(ocel, variant=JSONOCEL_TO_MDL, parameters=None):
    return VERSIONS[variant](ocel, parameters=parameters)
