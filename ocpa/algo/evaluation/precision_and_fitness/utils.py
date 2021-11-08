from collections import Counter
import networkx as nx


def calculate_preset(eog):
    preset = {}
    for e in eog.nodes:
        preset[e] = list(nx.ancestors(eog, e))
        # USE THIS FOR LARGE EVENT LOGS
        # stable speed also for later events, large logs with large connected components
        #preset[e] = [v for v in nx.dfs_predecessors(EOG, source=e).keys() if v!=e]
        # fast for small graphs/no connected component
        #preset[e] = [n for n in nx.traversal.bfs_tree(EOG, e, reverse=True) if n != e]
    return preset


def calculate_contexts_and_bindings(ocel):
    log = ocel.log.copy()
    object_types = ocel.object_types
    contexts = {}
    bindings = {}
    preset = calculate_preset(ocel.eog)
    log["event_objects"] = log.apply(
        lambda x: [(ot, o) for ot in object_types for o in x[ot]], axis=1)
    exploded_log = log.explode("event_objects")
    counter_e = 0
    for event in preset.keys():
        counter_e += 1
        context = {}
        obs = list(set().union(
            *log.loc[log["event_id"].isin(preset[event]+[event])]["event_objects"].to_list()))
        binding_sequence = log.loc[log["event_id"].isin(preset[event])].apply(lambda y: (y["event_activity"], {
            ot: [o for (ot_, o) in y["event_objects"] if ot_ == ot] for ot in object_types}), axis=1).values.tolist()
        for ob in obs:
            prefix = tuple(exploded_log[(exploded_log["event_objects"] == ob) & (
                exploded_log["event_id"].isin(preset[event]))]["event_activity"].to_list())
            if ob[0] not in context.keys():
                context[ob[0]] = Counter()
            context[ob[0]] += Counter([prefix])
        contexts[event] = context
        bindings[event] = binding_sequence
    return contexts, bindings
