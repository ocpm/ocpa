from ocpa.algo.ocel2_use_cases.e2o_qualifier_conformance import e2o_qualifier_conformance
from ocpa.objects.log.importer.ocel2.sqlite import factory as ocel_import_factory
from ocpa.objects.log.importer.ocel2.xml import factory as xmlocel_import_factory

# importing sqlite
ocel = ocel_import_factory.apply("/Users/gyunam/Documents/qprsim/sample/test_log_2.sqlite")
# importing xmlocel
# ocel = xmlocel_import_factory.apply("../../sample_logs/ocel2/xmlocel/ocel2.xml")
print(ocel.log.log)
