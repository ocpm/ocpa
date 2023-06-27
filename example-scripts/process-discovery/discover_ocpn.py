from ocpa.objects.log.importer.ocel import factory as ocel_import_factory
from ocpa.algo.discovery.ocpn import algorithm as ocpn_discovery_factory
from ocpa.visualization.oc_petri_net import factory as ocpn_vis_factory
filename = "/Users/gyunam/Documents/qprsim/sample/test_log.jsonocel"
ocel = ocel_import_factory.apply(file_path=filename)
ocpn = ocpn_discovery_factory.apply(ocel, parameters={"debug": False})
gviz = ocpn_vis_factory.apply(ocpn, parameters={'format': 'svg'})
ocpn_vis_factory.view(gviz)
