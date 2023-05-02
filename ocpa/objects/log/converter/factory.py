from ocpa.objects.log.converter.versions import jsonocel_to_csv
from ocpa.objects.log.converter.versions import df_to_ocel
from ocpa.objects.log.variants.obj import ObjectCentricEventLog

JSONOCEL_TO_CSV = "json_to_csv"
DF_TO_OCEL = "df_to_ocel"

VERSIONS = {JSONOCEL_TO_CSV: jsonocel_to_csv.apply, DF_TO_OCEL: df_to_ocel.apply}


def apply(
    ocel: ObjectCentricEventLog, variant=DF_TO_OCEL, parameters=None
) -> ObjectCentricEventLog:
    return VERSIONS[variant](ocel, parameters=parameters)
