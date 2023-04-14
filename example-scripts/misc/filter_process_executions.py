from ocpa.objects.log.importer.csv import factory as ocel_import_factory
from ocpa.algo.util.filtering.log import case_filtering
filename = "../../sample_logs/csv/BPI2017-Final.csv"
object_types = ["application", "offer"]
parameters = {"obj_names":object_types,
              "val_names":[],
              "act_name":"event_activity",
              "time_name":"event_timestamp",
              "sep":","}
ocel = ocel_import_factory.apply(file_path= filename,parameters = parameters)
print(ocel.log.log)
filtered = case_filtering.filter_process_executions(ocel, ocel.process_executions[0:8])
print(filtered.log.log)
export_df = filtered.log.log.sort_values(by='event_timestamp')
export_df.to_csv("BPI2017_filtered.csv",index = False)