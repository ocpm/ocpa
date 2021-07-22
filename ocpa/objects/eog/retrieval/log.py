import networkx as nx
from more_itertools import unique_everseen as mi_unique_everseen
def from_ocel(ocel, object_types = None):
    ocel = ocel.copy()
    if object_types == None:
        object_types = [c for c in ocel.columns if not c.startswith("event_")]
    EOG = nx.DiGraph()
    EOG.add_nodes_from(ocel["event_id"].to_list())
    #add edges for each shared object und dircetly follows
    all_obs = set()
    for ot in object_types:
        ocel[ot].apply(lambda x: [all_obs.add((ot,o)) for o in x])
    ocel["event_objects"] = ocel.apply(lambda x: [(ot,o) for ot in object_types for o in x[ot]], axis = 1)   
    exploded_log = ocel.explode("event_objects")
    for (ot,o) in all_obs:
        filtered_list = exploded_log[exploded_log["event_objects"] == (ot,o)]["event_id"].to_list()
        filtered_list = list(mi_unique_everseen(filtered_list))
        edge_list = [(a,b) for a,b in zip(filtered_list[:-1], filtered_list[1:])]
        EOG.add_edges_from(edge_list)
    ocel = ocel.drop(columns=["event_objects"])
    return EOG