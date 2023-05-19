from ocpa.algo.ocel2_use_cases.e2o_qualifier_conformance import e2o_qualifier_conformance
from ocpa.objects.log.importer.ocel2.sqlite import factory as ocel_import_factory
from ocpa.objects.log.importer.ocel2.xml import factory as xmlocel_import_factory

# importing sqlite
ocel = ocel_import_factory.apply("../../sample_logs/ocel2/sqlite/running-example.sqlite")
# importing xmlocel
# ocel = xmlocel_import_factory.apply("../../sample_logs/ocel2/xmlocel/ocel2.xml")
allowed, unallowed = e2o_qualifier_conformance(ocel, "send package", "employees", "forwarder", permitted_attributes = ["Warehousing"], attribute_lookup= "role")
print("Allowed values")
print(allowed)
print("Prohibited values")
print(unallowed)
