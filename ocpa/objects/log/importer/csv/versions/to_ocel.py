import pandas as pd
from ocpa.objects.log.ocel import OCEL
from ocpa.objects.log.variants.table import Table
from ocpa.objects.log.variants.graph import EventGraph
import ocpa.objects.log.converter.versions.df_to_ocel as obj_converter
import ocpa.objects.log.importer.csv.versions.to_df as df_importer
import ocpa.objects.log.importer.csv.util as csv_importer_utils
import ocpa.objects.log.variants.util.table as table_utils
import logging


def apply(filepath, parameters: dict, file_path_object_attribute_table=None) -> OCEL:
    ev_df = df_importer.apply(filepath, parameters)
    obj_df = None

    if file_path_object_attribute_table:
        delimiter = csv_importer_utils.get_csv_delimiter(file_path_object_attribute_table)
        obj_df = pd.read_csv(file_path_object_attribute_table, delimiter=delimiter)

    log = Table(ev_df, parameters=parameters, object_attributes=obj_df)
    logging.info("Table format successfully imported")
    obj = obj_converter.apply(ev_df, parameters={'objects_table':obj_df})
    logging.info("Object format successfully imported")
    graph = EventGraph(table_utils.eog_from_log(log))
    logging.info("Graph format successfully imported")
    ocel = OCEL(log, obj, graph, parameters)
    logging.info("OCEL constructed")
    return ocel
