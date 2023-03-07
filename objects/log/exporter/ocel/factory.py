import json

import pandas as pd
from dateutil import parser
from lxml import etree, objectify
import dateutil
from jsonschema import validate
import jsonschema
from datetime import datetime

from ocpa.objects.log.exporter.ocel.versions import export_ocel_json

OCEL_JSON = "ocel_json"

VERSIONS = {OCEL_JSON: export_ocel_json.apply}


def apply(ocel, file_path, variant=OCEL_JSON, parameters=None):
    '''
        Export an OCEL to JSONOCEL a file.

        Parameters
        ----------
        :param ocel: Object-centric event log
        :type ocel: :class:`OCEL <ocpa.objects.log.ocel.OCEL>`

        :param file_path: Path to save the jsonocel file.
        :type file_path: string


        :return: None
        :rtype: None
    '''
    return VERSIONS[variant](ocel, file_path, parameters=parameters)
