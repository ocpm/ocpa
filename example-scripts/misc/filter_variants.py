import ocpa
from ocpa.objects.log.importer.csv import factory as ocel_import_factory
from ocpa.algo.util.filtering.log.variant_filtering import filter_infrequent_variants
filename = "../../sample_logs/csv/BPI2017-Final.csv"
object_types = ["application", "offer"]
parameters = {"obj_names": object_types,
              "val_names": [],
              "act_name": "event_activity",
              "time_name": "event_timestamp",
              "sep": ",",
              "execution_extraction": ocpa.algo.util.process_executions.factory.LEAD_TYPE,
              "leading_type": object_types[0],
              "variant_calculation": ocpa.algo.util.variants.factory.TWO_PHASE}
ocel = ocel_import_factory.apply(file_path=filename, parameters=parameters)
filtered = filter_infrequent_variants(ocel, 0.1)
