import json
from jsonschema import validate
import jsonschema

from ocpa.objects.log.importer.ocel.versions import import_ocel_json
from ocpa.objects.log.importer.ocel.versions import import_ocel_xml
from ocpa.objects.log.ocel import OCEL

OCEL_JSON = "ocel_json"
OCEL_XML = "ocel_xml"

VERSIONS = {OCEL_JSON: import_ocel_json.apply,
            OCEL_XML: import_ocel_xml.apply}


def apply(file_path, variant=OCEL_JSON, parameters=None) -> OCEL:
    return VERSIONS[variant](file_path, parameters=parameters)
