from ocpa.objects.log.importer.ocel import factory as ocel_import_factory

filename = "../../sample_logs/jsonocel/p2p-normal.jsonocel"
ocel = ocel_import_factory.apply(filename)
