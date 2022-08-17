import ocpa
from ocpa.objects.log.importer.mdl import factory as ocel_import_factory
from ocpa.algo.filtering.log.variant_filtering import filter_infrequent_variants
filename = "/Users/gyunam/Documents/sample_logs/mdl/BPI2017-Full.csv"
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
print(filtered.log.log)
filtered.log.log.to_csv("./filter_variant.csv")

"""
Traceback (most recent call last):
  File "example-scripts/filter_variants.py", line 15, in <module>
    filtered = filter_infrequent_variants(ocel, 0.1)
  File "/Users/gyunam/Documents/ocpa-core/ocpa/algo/filtering/log/variant_filtering.py", line 21, in filter_infrequent_variants
    execution_extraction=ocel._execution_extraction, leading_object_type=ocel._leading_type)
AttributeError: 'OCEL' object has no attribute '_leading_type'
"""
