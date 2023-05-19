from ocpa.objects.log.importer.ocel import factory as ocel_import_factory

filename = "../../sample_logs/jsonocel/p2p-normal.jsonocel"
parameters = {"execution_extraction": "leading_type",
              "leading_type": "GDSRCPT",
              "variant_calculation": "two_phase",
              "exact_variant_calculation": True}
ocel = ocel_import_factory.apply(filename,parameters=parameters)