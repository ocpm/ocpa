from ocpa.objects.log.importer.ocel import factory as ocel_import_factory
from ocpa.algo.discovery.ocpn import algorithm as ocpn_discovery_factory
from ocpa.visualization.oc_petri_net import factory as ocpn_vis_factory
from ocpa.algo.enhancement.token_replay_based_performance import algorithm as performance_factory

filename = "../../sample_logs/jsonocel/p2p-2023.jsonocel"
ocel = ocel_import_factory.apply(filename)
ocpn = ocpn_discovery_factory.apply(ocel)
diag_params = {'measures': ['act_freq', 'arc_freq', 'object_count', 'waiting_time', 'service_time', 'sojourn_time', 'synchronization_time', 'pooling_time', 'lagging_time', 'flow_time'], 'agg': [
    'mean', 'min', 'max'], 'format': 'svg'}
diag = performance_factory.apply(ocpn, ocel, parameters=diag_params)
print(f'Diagnostics: {diag}')
gviz = ocpn_vis_factory.apply(
    ocpn, diagnostics=diag, variant="annotated_with_opera", parameters=diag_params)
ocpn_vis_factory.view(gviz)
