from ocpa.objects.log.importer.mdl.versions import to_df
from ocpa.objects.log.importer.mdl.versions import to_obj
from ocpa.objects.log.importer.mdl.versions import to_ocel

TO_DF = "to_df"
TO_OBJ = "to_obj"
TO_OCEL = "to_ocel"

VERSIONS = {TO_DF: to_df.apply,
            TO_OBJ: to_obj.apply,
            TO_OCEL: to_ocel.apply}


def apply(file_path, variant=TO_OCEL, parameters=None):
    return VERSIONS[variant](file_path, parameters=parameters)
