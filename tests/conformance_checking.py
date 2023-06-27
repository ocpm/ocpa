from ocpa.objects.log.importer.ocel import factory as ocel_import_factory
from ocpa.algo.conformance.precision_and_fitness import evaluator as quality_measure_factory
from ocpa.algo.discovery.ocpn import algorithm as ocpn_discovery_factory
from ocpa.visualization.oc_petri_net import factory as ocpn_vis_factory

def test_process_execution_extraction():
    filename = "sample_logs/jsonocel/p2p-normal.jsonocel"
    ocel = ocel_import_factory.apply(filename)
    ocpn = ocpn_discovery_factory.apply(ocel, parameters={"debug": False})
    ocpn = ocpn_discovery_factory.apply(ocel, parameters={"debug": False})
    gviz = ocpn_vis_factory.apply(ocpn, parameters={'format': 'svg'})
    ocpn_vis_factory.view(gviz)
    precision, fitness = quality_measure_factory.apply(ocel, ocpn)
    print(precision, fitness)
    assert 0.81 < precision < 0.83
    assert fitness == 1.0

if __name__ == "__main__":
    test_process_execution_extraction()
