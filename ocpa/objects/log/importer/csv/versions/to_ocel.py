import pandas as pd
from ocpa.objects.log.ocel import OCEL
from ocpa.objects.log.variants.table import Table
from ocpa.objects.log.variants.graph import EventGraph
import ocpa.objects.log.importer.csv.versions.to_obj as obj_importer
import ocpa.objects.log.importer.csv.versions.to_df as df_importer
import ocpa.objects.log.variants.util.table as table_utils
from typing import Dict


def apply(filepath, parameters: Dict, file_path_object_attribute_table = None) -> OCEL:
    df = df_importer.apply(filepath, parameters)
    obj_df = None
    if file_path_object_attribute_table:
        obj_df = pd.read_csv(file_path_object_attribute_table)
    log = Table(df, parameters=parameters,object_attributes=obj_df)
    obj = obj_importer.apply(df, parameters=parameters)
    graph = EventGraph(table_utils.eog_from_log(log))
    ocel = OCEL(log, obj, graph, parameters)
    return ocel
