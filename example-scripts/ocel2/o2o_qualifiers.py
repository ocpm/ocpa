from ocpa.algo.ocel2_use_cases.o2o_qualifier_conformance import check_o2o_qualifier_conformance
from ocpa.objects.log.importer.ocel2.sqlite import factory as ocel_import_factory

ocel = ocel_import_factory.apply("../../sample_logs/ocel2/sqlite/running-example.sqlite")
allowed, unallowed = check_o2o_qualifier_conformance(ocel, "confirm order", "customers", "employees", allowed_qualifiers = ["primarySalesRep","secondarySalesRep"])
print("Allowed Qualifiers")
print(allowed)
print("Prohibited Qualifiers")
print(unallowed)
