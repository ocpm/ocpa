import pandas as pd
from ocpa.objects.log.ocel import OCEL
from ocpa.objects.log.variants.table import Table
from ocpa.objects.log.variants.graph import EventGraph
import ocpa.objects.log.importer.mdl.versions.to_obj as obj_importer
import ocpa.objects.log.importer.mdl.versions.to_df as df_importer
import ocpa.objects.log.variants.util.table as table_utils
from typing import Dict

# TODO: implement apply function


def apply(filepath, parameters: Dict) -> OCEL:
    df = df_importer.apply(filepath,parameters)[:200]
    log = Table(df, parameters = parameters)
    obj = obj_importer.apply(df, parameters=parameters)
    graph = EventGraph(table_utils.eog_from_log(log))
    ocel = OCEL(log,obj,graph,parameters)
    return ocel