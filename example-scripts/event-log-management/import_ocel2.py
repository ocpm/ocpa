from ocpa.objects.log.importer.ocel2.sqlite import factory as ocel_import_factory

ocel = ocel_import_factory.apply("../../sample_logs/ocel2/sqlite/ocel20_example.sqlite")
print(len(ocel.process_executions))
print(len(ocel.o2o_graph.graph.nodes()))
print(ocel.change_table)
print(ocel.graph.eog.nodes["e1"])