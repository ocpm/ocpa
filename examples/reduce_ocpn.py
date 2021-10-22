from ocpa.objects.log.importer.ocel import factory as ocel_import_factory
from ocpa.algo.discovery.ocpn import algorithm as ocpn_discovery_factory
from ocpa.visualization.oc_petri_net import factory as pn_vis_factory
from ocpa.algo.conformance.token_based_replay import algorithm as ocpn_conformance_factory
from ocpa.objects.event_graph.retrieval import algorithm as event_graph_factory
from ocpa.objects.correlated_event_graph.retrieval import algorithm as correlated_event_graph_factory

from ocpa.algo.projection.ocpn import algorithm as ocpn_project_factory
from ocpa.algo.filtering.event_graph import algorithm as event_graph_filtering_factory

from ocpa.algo.reduction.ocpn import algorithm as ocpn_reduction_factory

from ocpa.algo.enhancement.event_graph_based_performance import algorithm as performance_factory

filename = "../example_logs/jsonocel/simulated-logs.jsonocel"
df = ocel_import_factory.apply(filename, parameters={'return_df': True})

ocel = ocel_import_factory.apply(filename)

event_df = df[0]
# print(event_df)

ots = ["order", "item", "route"]
eg = event_graph_factory.apply(ocel)

cegs = correlated_event_graph_factory.apply(eg)

ocpn = ocpn_discovery_factory.apply(event_df)

parameters = dict()
parameters['selected_object_types'] = ["order"]
ocpn = ocpn_project_factory.apply(ocpn, parameters=parameters)

# gviz = pn_vis_factory.apply(
#     ocpn, variant="control_flow", parameters={"format": "svg"})
# pn_vis_factory.view(gviz)

# selected_transition_labels = {
#     "send_notification", "send_invoice", "place_order"}
# selected_transition_labels = {"place_order"}
# selected_transition_labels = {"send_notification", "skip_send_notification", "collect_payment",
#   "skip_approve_picking", "place_order", "approve_picking", "pick_item", "end_route", "start_route"}
selected_transition_labels = {"send_notification", "skip_send_notification"}
parameters = dict()
parameters['selected_transition_labels'] = selected_transition_labels
reduced_ocpn = ocpn_project_factory.apply(
    ocpn, variant="hiding", parameters=parameters)

# reduced_ocpn, log = ocpn_reduction_factory.apply(new_ocpn)

gviz = pn_vis_factory.apply(
    reduced_ocpn, variant="control_flow", parameters={"format": "svg"})
pn_vis_factory.view(gviz)


# # gviz = pn_vis_factory.apply(
# #     new_ocpn, variant="control_flow", parameters={"format": "svg"})
# # pn_vis_factory.view(gviz)

# parameters = dict()
# new_cegs = event_graph_filtering_factory.apply(
#     ocpn, cegs, variant='object_types')

# # for ceg in new_cegs:
# #     print(ceg.graph.edges)

# # selected_transition_labels = {"send_notification", "send_invoice",
# #                               "place_order"}
# # parameters = dict()
# # parameters['selected_transition_labels'] = selected_transition_labels
# # new_ocpn = ocpn_project_factory.apply(
# #     ocpn, variant="subprocess", parameters=parameters)


# # new_cegs = event_graph_filtering_factory.apply(
# #     new_ocpn, cegs, variant='subprocess')

# perf_parameters = dict()
# perf_parameters['perf_metric'] = "object_freq"
# perf_parameters['agg'] = "avg"
# result = performance_factory.apply(ocpn, cegs, parameters=perf_parameters)
# print(result)
