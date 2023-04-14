from ocpa.algo.ocel2_use_cases.e2o_qualifier_conformance import e2o_qualifier_conformance
from ocpa.objects.log.importer.ocel2.sqlite import factory as ocel_import_factory

ocel = ocel_import_factory.apply("../../sample_logs/ocel2/sqlite/running-example.sqlite")
allowed, unallowed = e2o_qualifier_conformance(ocel, "send package", "employees", "forwarder", permitted_attributes = ["Warehousing"], attribute_lookup= "role")
print("Allowed values")
print(allowed)
print("Prohibited values")
print(unallowed)
