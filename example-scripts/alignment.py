from ocpa.objects.log.importer.ocel import factory as ocel_import_factory
from ocpa.objects.log.exporter.ocel import factory as ocel_export_factory
filename = "sample_logs/jsonocel/order_process.jsonocel"
ocel = ocel_import_factory.apply(filename)

from ocpa.algo.discovery.ocpn import algorithm as ocpn_discovery_factory
from ocpa.visualization.oc_petri_net import factory as ocpn_vis_factory
ocpn = ocpn_discovery_factory.apply(ocel, parameters={"debug": False})

from ocpa.algo.conformance.alignments import algorithm as alignment_factory

alignments_ocpn = alignment_factory.calculate_oc_alignments(ocel, ocpn)