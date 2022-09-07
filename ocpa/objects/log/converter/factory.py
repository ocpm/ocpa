from ocpa.objects.log.converter.versions import jsonocel_to_csv
from ocpa.objects.log.converter.versions import csv_to_ocel

JSONOCEL_TO_MDL = "json_to_mdl"
CSV_TO_OCEL = "csv_to_ocel"

VERSIONS = {JSONOCEL_TO_MDL: jsonocel_to_csv.apply,
            CSV_TO_OCEL: csv_to_ocel.apply}


def apply(ocel, variant=JSONOCEL_TO_MDL, parameters=None):
    return VERSIONS[variant](ocel, parameters=parameters)
