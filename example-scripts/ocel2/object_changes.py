from ocpa.algo.ocel2_use_cases.object_change_tables import plot_attribute_over_time
from ocpa.objects.log.importer.ocel2.sqlite import factory as ocel_import_factory

ocel = ocel_import_factory.apply("../../sample_logs/ocel2/sqlite/running-example.sqlite")
print(len(ocel.process_executions))
print(len(ocel.o2o_graph.graph.nodes()))
plot_attribute_over_time(ocel, "products", "price", "object_id", "ocel_aggregated_changes", title="Observing Inflation in Product Prices")
