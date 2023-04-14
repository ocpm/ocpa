from ocpa.objects.log.importer.ocel2.sqlite.versions import import_ocel2_sqlite
from ocpa.objects.log.ocel import OCEL


OCEL2_SQLITE = "ocel2_sqlite"

VERSIONS = {OCEL2_SQLITE: import_ocel2_sqlite.apply}


def apply(file_path, variant=OCEL2_SQLITE, parameters={}) -> OCEL:
    return VERSIONS[variant](file_path, parameters=parameters)