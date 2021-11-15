import json

import pandas as pd
from dateutil import parser
from lxml import etree, objectify
import dateutil
from jsonschema import validate
import jsonschema
from datetime import datetime

from ocpa.objects.log.importer.ocel.versions import import_ocel_json
from ocpa.objects.log.importer.ocel.versions import import_ocel_xml

OCEL_JSON = "ocel_json"
OCEL_XML = "ocel_xml"

VERSIONS = {OCEL_JSON: import_ocel_json.apply,
            OCEL_XML: import_ocel_xml.apply}


def apply(file_path, variant=OCEL_JSON, parameters=None):
    return VERSIONS[variant](file_path, parameters=parameters)


# def apply(file_path, return_obj_df=None, parameters=None):
#     if "xml" in file_path:
#         return apply_xml(file_path, return_obj_df=return_obj_df, parameters=parameters)
#     elif "json" in file_path.lower():
#         return apply_json(file_path, return_obj_df=return_obj_df, parameters=parameters)


def validate_with_schema(file_path, schema_path):
    if "json" in file_path.lower():
        file_content = json.load(open(file_path, "rb"))
        schema_content = json.load(open(schema_path, "rb"))
        try:
            validate(instance=file_content, schema=schema_content)
            return True
        except jsonschema.exceptions.ValidationError as err:
            return False
        return False
    elif "xml" in file_path:
        try:
            import lxml
            xml_file = lxml.etree.parse(file_path)
            xml_validator = lxml.etree.XMLSchema(file=schema_path)
            is_valid = xml_validator.validate(xml_file)
            return is_valid
        except:
            return False
