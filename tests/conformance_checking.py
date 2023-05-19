import unittest
from ocpa.objects.log.importer.ocel import factory as ocel_import_factory
from ocpa.algo.conformance.precision_and_fitness import evaluator as quality_measure_factory
from ocpa.algo.discovery.ocpn import algorithm as ocpn_discovery_factory
class ConformanceCheckingTests(unittest.TestCase):

    def test_process_execution_extraction(self):
        filename = "../sample_logs/jsonocel/p2p-normal.jsonocel"
        ocel = ocel_import_factory.apply(filename)
        ocpn = ocpn_discovery_factory.apply(ocel, parameters={"debug": False})
        precision, fitness = quality_measure_factory.apply(ocel, ocpn)
        self.assertTrue(0.81 < precision < 0.83)
        self.assertEqual(fitness, 1.0)

if __name__ == '__main__':
    unittest.main()