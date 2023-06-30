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


def apply(file_path, variant=OCEL_JSON, parameters=None, file_path_object_attribute_table = None) -> OCEL:
    '''
        Reads a jsonocel or jsonxml and transforms it into an OCEL object.

        Parameters
        ----------
        file_path: string
            Path to the jsonocel or jsonxml file.
        variant: string
            Method to import OCEL (default = OCEL_JSON)
        parameters: dict
            parameters that will be used for importing the log and for log settings:
                - execution_extraction: Optional, execution extraction technique to extract process executions (cases) in the log, possible values:
                    - :data:`ocpa.algo.util.process_executions.factory.CONN_COMP <ocpa.algo.util.process_executions.factory.CONN_COMP>` (default)
                    - :data:`ocpa.algo.util.process_executions.factory.LEAD_TYPE <ocpa.algo.util.process_executions.factory.LEAD_TPYE>`
                - variant_calculation: Optional, variant calculation technique to determine variants in the log, possible values:
                    - :data:`ocpa.algo.util.variants.factory.TWO_PHASE <ocpa.algo.util.variants.factory.TWO_PHASE>` (default)
                    - :data:`ocpa.algo.util.variants.factory.ONE_PHASE <ocpa.algo.util.variants.factory.ONE_PHASE>`
                - timeout: Optional, seconds until variant calculation timeout.
                - leading_type: Optional, only used when execution_extraction=ocpa.algo.util.process_executions.factory.LEAD_TYPE, determines the leading type of the object types
                - exact_variant_calculation: Optional, boolean value for switching on the refinement of initial classes in the two-phase variant calculation. False (default) will most likely provide an approximation.


        Returns
        -------
        OCEL
        '''
    return VERSIONS[variant](file_path, parameters=parameters, file_path_object_attribute_table = None)
