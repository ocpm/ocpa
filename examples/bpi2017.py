import matplotlib.pyplot as plt
import networkx as nx
from ocpa.objects.log.importer.ocel import factory as ocel_import_factory
from ocpa.objects.log.importer.mdl import factory as mdl_import_factory
from ocpa.objects.log.converter import factory as log_convert_factory
from ocpa.algo.discovery.ocpn import algorithm as ocpn_discovery_factory
from ocpa.visualization.oc_petri_net import factory as pn_vis_factory
from ocpa.objects.oc_petri_net.obj import Subprocess
from ocpa.objects.event_graph.retrieval import algorithm as event_graph_factory
from ocpa.objects.correlated_event_graph.retrieval import algorithm as correlated_event_graph_factory

from ocpa.algo.projection.ocpn import algorithm as ocpn_project_factory

from ocpa.algo.enhancement.event_graph_based_performance import algorithm as performance_factory

import pandas as pd

# # sampling
# filename = "/Users/gyunam/Documents/ocpa-core/example_logs/mdl/Full.csv"
# df = pd.read_csv(filename)
# applications = set(df["case"])
# num_apps = len(applications)
# sample_size = int(num_apps*0.001)
# samples = list(applications)[:sample_size]
# sample_df = df.loc[df["case"].isin(samples)]
# sample_df.reset_index(inplace=True)
# sample_df = sample_df.rename(columns={"index": "event_id", "case": "ApplicationID", "event": "event_activity",
#                                       "completeTime": "event_timestamp", "startTime": "event_start_timestamp"})

# sample_df = sample_df[["event_id", "event_activity", "event_timestamp",
#                        "event_start_timestamp", "ApplicationID", "OfferID"]]
# for i, row in sample_df.iterrows():
#     if row["event_activity"] in ["O_Returned", "O_Sent"]:
#         # application_id = None
#         sample_df.at[i,'ApplicationID'] = None
#     if row["event_activity"] in ["O_Create"]:
#         # offer_id = None
#         sample_df.at[i,'OfferID'] = None
#     if row["ApplicationID"] is not None:
#         sample_df.at[i,'ApplicationID'] = [row["ApplicationID"]]

#     if row["OfferID"] is not None:
#         sample_df.at[i,'OfferID'] = [row["OfferID"]]
# print(sample_df)
# sample_df.to_csv(
#     "/Users/gyunam/Documents/ocpa-core/example_logs/mdl/Sample.csv")


filename = "/Users/gyunam/Documents/ocpa-core/example_logs/mdl/BPI2017-Top10-2.csv"
df = pd.read_csv(filename, dtype=str)
del df["Unnamed: 0"]
# del df["event_start_timestamp"]
del df["CaseID"]
del df["EventID"]
del df["event_variant"]

parameters = {
    "obj_names": ["A", "O"],
    "val_names": [],
    "time_name": "event_timestamp",
    "act_name": "event_activity",
    "start_time": "event_start_timestamp"
}

# event_df = mdl_import_factory.apply(df, parameters={'return_df': True})
# print(event_df)


ocel = mdl_import_factory.apply(
    df, variant="to_obj", parameters=parameters)

eg = event_graph_factory.apply(ocel)

cegs = correlated_event_graph_factory.apply(eg)

initial_ceg = list(cegs)[1]
a = len(set(
    [initial_ceg.ovmap[oi].type for e in initial_ceg.graph.nodes for oi in e.omap]))
print(a)

# for i in range(1):
#     graph = list(cegs)[i].graph
#     nx.draw(graph, with_labels=True)
#     plt.show()

# ocpn = ocpn_discovery_factory.apply(event_df)

# gviz = pn_vis_factory.apply(
#     ocpn, variant="control_flow", parameters={"format": "svg"})
# pn_vis_factory.view(gviz)
