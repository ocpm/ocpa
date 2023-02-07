from ocpa.objects.log.importer.csv import factory as ocel_import_factory
filename = "../../sample_logs/csv/BPI2017-Final.csv"
object_types = ["application", "offer"]
parameters = {"obj_names": object_types,
              "val_names": [],
              "act_name": "event_activity",
              "time_name": "event_timestamp",
              "sep": ","}
ocel = ocel_import_factory.apply(file_path=filename, parameters=parameters)
