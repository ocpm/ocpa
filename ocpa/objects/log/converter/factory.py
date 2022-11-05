from ocpa.objects.log.converter.versions import jsonocel_to_csv
from ocpa.objects.log.converter.versions import df_to_ocel

JSONOCEL_TO_MDL = "json_to_mdl"
DF_TO_OCEL = "df_to_ocel"

VERSIONS = {JSONOCEL_TO_MDL: jsonocel_to_csv.apply,
            DF_TO_OCEL: df_to_ocel.apply}


def apply(ocel, variant=DF_TO_OCEL, parameters=None):
    return VERSIONS[variant](ocel, parameters=parameters)
