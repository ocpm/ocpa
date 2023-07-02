from ocpa.objects.log.importer.ocel import factory as ocel_import_factory
from ocpa.algo.conformance.precision_and_fitness import evaluator as quality_measure_factory
from ocpa.algo.discovery.ocpn import algorithm as ocpn_discovery_factory

filename = "/Users/gyunam/Documents/qprsim/sample/test_log.jsonocel"
ocel = ocel_import_factory.apply(filename)
ocpn = ocpn_discovery_factory.apply(ocel, parameters = {"debug":True})
precision, fitness = quality_measure_factory.apply(ocel, ocpn)
print("Precision of IM-discovered net: "+str(precision))
print("Fitness of IM-discovered net: "+str(fitness))
