from ocpa.objects.log.importer.ocel import factory as ocel_import_factory
from ocpa.algo.util.filtering.log import case_filtering
filename = "../../sample_logs/jsonocel/p2p-normal.jsonocel"
ocel = ocel_import_factory.apply(filename)
print(ocel.log.log)
filtered = case_filtering.filter_process_executions(ocel, ocel.process_executions[0:10])
print(filtered.log.log)