from ocpa.objects.log.importer.csv.versions import to_df, to_obj, to_ocel
from ocpa.objects.log.ocel import OCEL

TO_DF = "to_df"
TO_OBJ = "to_obj"
TO_OCEL = "to_ocel"

VERSIONS = {TO_DF: to_df.apply, TO_OBJ: to_obj.apply, TO_OCEL: to_ocel.apply}


def apply(
    file_path, variant=TO_OCEL, parameters=None, file_path_object_attribute_table=None
) -> OCEL:
    """
    Reads a csv and transforms it into an OCEL object.

    Parameters
    ----------
    file_path: string
        Path to the csv file.
    variant: string
        Method to import OCEL (default = TO_OCEL) (will be removed)
    parameters: dict
        parameters that will be used for importing the log and for log settings:
            - obj_names: List of object types (columns in CSV)
            - val_names: List of attribute names (columns in CSV)
            - act_name: Column name of event's activity
            - time_name: Column name of event's timestamp
            - start_timestamp: Optional, column name of event's start timestamp; If missing, replaced by time_name.
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
    """

    return VERSIONS[variant](
        file_path,
        parameters=parameters,
        file_path_object_attribute_table=file_path_object_attribute_table,
    )
