from ocpa.objects.log.importer.ocel import factory as ocel_import_factory
from ocpa.objects.log.exporter.ocel import factory as ocel_export_factory
filename = "../../sample_logs/jsonocel/p2p-normal.jsonocel"
ocel = ocel_import_factory.apply(filename)
ocel_export_factory.apply(
    ocel, './exported-p2p-normal_export.jsonocel')
