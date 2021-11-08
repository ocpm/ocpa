from ocpa.objects.log.importer.mdl.versions import to_df
from ocpa.objects.log.importer.mdl.versions import to_obj

TO_DF = "to_df"
TO_OBJ = "to_obj"

VERSIONS = {TO_DF: to_df.apply,
            TO_OBJ: to_obj.apply}


def apply(file_path, variant=TO_DF, parameters=None):
    return VERSIONS[variant](file_path, parameters=parameters)
