import pandas as pd

from ocpa.objects.log.importer.mdl import factory as mdl_import_factory
from ocpa.algo.discovery.ocpn import algorithm as ocpn_discovery_factory
from ocpa.visualization.oc_petri_net import factory as pn_vis_factory
from ocpa.algo.conformance.token_based_replay import algorithm as ocpn_conformance_factory
from ocpa.objects.event_graph.retrieval import algorithm as event_graph_factory
from ocpa.objects.correlated_event_graph.retrieval import algorithm as correlated_event_graph_factory

from ocpa.algo.projection.ocpn import algorithm as ocpn_project_factory
from ocpa.algo.filtering.event_graph import algorithm as event_graph_filtering_factory

from ocpa.algo.reduction.ocpn import algorithm as ocpn_reduction_factory

from ocpa.algo.enhancement.event_graph_based_performance import algorithm as performance_factory

filename = "/Users/gyunam/Documents/ocpa-core/example_logs/mdl/BPI2017-Top3.csv"
ots = ["ApplicationID", "OfferID"]
df = pd.read_csv(filename)
del df["Unnamed: 0"]

df = mdl_import_factory.apply(df, parameters={'return_df': True})
print(df)

ocpn = ocpn_discovery_factory.apply(df)

parameters = dict()
parameters['selected_object_types'] = ["ApplicationID"]
reduced_ocpn = ocpn_project_factory.apply(
    ocpn, variant="object_types", parameters=parameters)

selected_transition_labels = {
    "A_Create Application", "A_Submitted", "A_Concept", "W_Complete application", "A_Accepted"}
parameters = dict()
parameters['selected_transition_labels'] = selected_transition_labels
reduced_ocpn = ocpn_project_factory.apply(
    reduced_ocpn, variant="hiding", parameters=parameters)

gviz = pn_vis_factory.apply(
    reduced_ocpn, variant="control_flow", parameters={"format": "svg"})
pn_vis_factory.view(gviz)
