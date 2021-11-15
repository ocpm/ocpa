from pm4py.objects.log.exporter.xes import exporter as xes_exporter
import pandas as pd
from pm4py.objects.log.util import dataframe_utils
from pm4py.objects.conversion.log import converter as log_converter

path_to_csv_file = "/Users/gyunam/Documents/ocpa-core/example_logs/mdl/BPI2017-Top3.csv"
log_csv = pd.read_csv(path_to_csv_file, sep=',')

# ots = ["ApplicationID", "OfferID"]

# for ot in ots:
#     log_csv[ot] = log_csv[ot].map(
#         lambda x: [y.strip() for y in x.split(',')] if isinstance(x, str) else [])
parameters = {
    log_converter.Variants.TO_EVENT_LOG.value.Parameters.CASE_ID_KEY: 'CaseID'}

log_csv = dataframe_utils.convert_timestamp_columns_in_df(log_csv)

log_csv = log_csv.sort_values("event_timestamp")
event_log = log_converter.apply(
    log_csv, parameters=parameters, variant=log_converter.Variants.TO_EVENT_LOG)
print(event_log)

xes_exporter.apply(event_log, "../example_logs/BPI2017-Top3.xes")
