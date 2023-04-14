from ocpa.algo.ocel2_use_cases.o2o_qualifier_conformance import check_o2o_qualifier_conformance
from ocpa.objects.log.importer.ocel2.sqlite import factory as ocel_import_factory

ocel = ocel_import_factory.apply("../../sample_logs/ocel2/sqlite/running-example.sqlite")
print(len(ocel.process_executions))
print(len(ocel.o2o_graph.graph.nodes()))
allo, unall = check_o2o_qualifier_conformance(ocel, "confirm order", "customers", "employees", allowed_qualifiers = ["primarySalesRep","secondarySalesRep"])
print(allo)
print(unall)

