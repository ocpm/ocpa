import ocpa.objects.eog.retrieval.log as event_object_graph_extractor
import ocpa.objects.eog.util.event_preset as event_preset
from collections import Counter
import networkx as nx
from itertools import groupby


def calculate_preset(eog):
    preset = {}
    for e in eog.nodes:
        preset[e] = list(nx.ancestors(eog,e))
        #USE THIS FOR LARGE EVENT LOGS
        #stable speed also for later events, large logs with large connected components
        #preset[e] = [v for v in nx.dfs_predecessors(EOG, source=e).keys() if v!=e]
        #fast for small graphs/no connected component
        #preset[e] = [n for n in nx.traversal.bfs_tree(EOG, e, reverse=True) if n != e]
    return preset


def calculate_contexts_and_bindings(ocel):
    log = ocel.log.copy()
    object_types = ocel.object_types
    contexts = {}
    bindings = {}
    #print("preset calc")
    preset = calculate_preset(ocel.eog)
    #print("applying")
    log["event_objects"] = log.apply(lambda x: [(ot,o) for ot in object_types for o in x[ot]], axis = 1)
    #print("Exploding")
    exploded_log = log.explode("event_objects")
    #print("Exploded")
    counter_e=0
    for event in preset.keys():
        #if counter_e % 250 == 0:
        #    print("Event "+str(counter_e))
        counter_e+=1
        context = {}
        #take all preset and project onto the sequences for each object
        #extract all object of the prefix
        obs = list(set().union(*log.loc[log["event_id"].isin(preset[event]+[event])]["event_objects"].to_list()))
        #print(ocel.loc[ocel["event_id"].isin(preset[event])].apply(lambda y: (y["event_activity"], { k : [*map(lambda v: v[1], values)] for k, values in groupby(sorted(y["event_objects"], key=lambda x: x[0]), lambda x: x[0])}), axis = 1).values.tolist())
        #binding_sequence = ocel.loc[ocel["event_id"].isin(preset[event])].apply(lambda y: (y["event_activity"], { k : [*map(lambda v: v[1], values)] for k, values in groupby(sorted(y["event_objects"], key=lambda x: x[0]), lambda x: x[0])}), axis = 1).values.tolist()
        #print(event)
        #print(preset[event])
        #print(ocel.loc[ocel["event_id"].isin(preset[event])]) 
        binding_sequence = log.loc[log["event_id"].isin(preset[event])].apply(lambda y: (y["event_activity"], { ot : [o for (ot_,o) in y["event_objects"] if ot_ == ot] for ot in object_types}), axis = 1).values.tolist()
        for ob in obs:
            prefix = tuple(exploded_log[(exploded_log["event_objects"] == ob) & (exploded_log["event_id"].isin(preset[event]))]["event_activity"].to_list())
            if ob[0] not in context.keys():
                context[ob[0]] = Counter()
            context[ob[0]]+=Counter([prefix])
        contexts[event] = context
        bindings[event] = binding_sequence
    return contexts, bindings
        