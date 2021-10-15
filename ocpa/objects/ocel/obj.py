import pandas as pd
import networkx as nx
from more_itertools import unique_everseen as mi_unique_everseen


class OCEL():
    def __init__(self, log, object_types=None, precalc = False):
        self._log = log
        if object_types != None:
            self._object_types = object_types
        else:
            self._object_types = [c for c in self._log.columns if not c.startswith("event_")]
        if precalc:
            self._eog = self.eog_from_log()
            self._cases = self.calculate_cases()
            self._variants, self._variant_frequency = self.calculate_variants()
        else:
            self._eog = None
            self._cases = None
            self._variants = None
            self._variant_frequency = None

    def _get_log(self):
        return self._log

    def _set_log(self, log):
        self._log = log

    def _get_eog(self):
        if self._eog == None:
            self._eog = self.eog_from_log()
        return self._eog

    def _get_cases(self):
        if self._cases == None:
            self._cases = self.calculate_cases()
        return self._cases

    def _get_variants(self):
        if self._variants == None:
            self._variants, self._variant_frequency = self.calculate_variants()
        return self._variants

    def _get_variant_frequency(self):
        if self._variant_frequency == None:
            self._variants, self._variant_frequency = self.calculate_variants()
        return self._variant_frequency

    def _get_object_types(self):
        return self._object_types

    def _set_object_types(self, object_types):
        self.object_types = object_types


    log = property(_get_log, _set_log)
    object_types = property(_get_object_types, _set_object_types)
    eog = property(_get_eog)
    cases = property(_get_cases)
    variants = property(_get_variants)
    variant_frequency = property(_get_variant_frequency)

    def eog_from_log(self):
        ocel = self.log.copy()
        EOG = nx.DiGraph()
        EOG.add_nodes_from(ocel["event_id"].to_list())
        # add edges for each shared object und dircetly follows
        all_obs = set()
        for ot in self.object_types:
            ocel[ot].apply(lambda x: [all_obs.add((ot, o)) for o in x])
        ocel["event_objects"] = ocel.apply(lambda x: [(ot, o) for ot in self.object_types for o in x[ot]], axis=1)
        exploded_log = ocel.explode("event_objects")
        for (ot, o) in all_obs:
            filtered_list = exploded_log[exploded_log["event_objects"] == (ot, o)]["event_id"].to_list()
            filtered_list = list(mi_unique_everseen(filtered_list))
            edge_list = [(a, b) for a, b in zip(filtered_list[:-1], filtered_list[1:])]
            EOG.add_edges_from(edge_list)
        ocel = ocel.drop(columns=["event_objects"])
        return EOG

    def calculate_cases(self):
        # Add the possibility to remove edges
        cases = sorted(nx.weakly_connected_components(self.eog), key=len, reverse=True)
        return cases

    def _project_subgraph_on_activity(self, v_g):
        # grpah mit aktivitäten
        mapping = dict(zip(self.log["event_id"], self.log["event_activity"]))
        mapping_objects = dict(zip(self.log["event_id"], self.log["event_objects"]))
        for node in v_g.nodes():
            v_g.nodes[node]['label'] = mapping[node]
        for edge in v_g.edges():
            source, target = edge
            v_g.edges[edge]['type'] = ": ".join(
                [e[0] for e in sorted(list(set(mapping_objects[source]).intersection(set(mapping_objects[target]))))])
            v_g.edges[edge]['label'] = ": ".join(
                [str(e) for e in sorted(list(set(mapping_objects[source]).intersection(set(mapping_objects[target]))))])
        return v_g

    def calculate_variants(self):
        variants = None
        self.log["event_objects"] = self.log.apply(lambda x: [(ot, o) for ot in self.object_types for o in x[ot]], axis=1)
        variants_dict = dict()
        variant_graphs = dict()
        case_id = 0
        for v_g in self.cases:
            case = self._project_subgraph_on_activity(self.eog.subgraph(v_g))
            variant = nx.weisfeiler_lehman_graph_hash(case, node_attr="label",
                                                      edge_attr="type")  # sorted(list(nx.generate_edgelist(case)))
            variant_string = ','.join(variant)
            if variant_string not in variants_dict:
                variants_dict[variant_string] = []
                variant_graphs[variant_string] = case  # EOG.subgraph(v_g)#case
            variants_dict[variant_string].append(case_id)
            case_id += 1
        variant_frequencies = {v: len(variants_dict[v]) / len(self.cases) for v in variants_dict.keys()}
        variants, v_freq_list = map(list,
                                    zip(*sorted(list(variant_frequencies.items()), key=lambda x: x[1], reverse=True)))
        for v_id in range(0, len(variants)):
            v = variants[v_id]
            cases = [self.cases[c_id] for c_id in variants_dict[v]]
            events = list(set().union(*cases))
            self.log.loc[self.log["event_id"].isin(events), "event_variant"] = v_id
        self.log["event_variant"] = self.log["event_variant"].astype(int)
        #for i in range(0, 10):
        #    print("Class number " + str(i + 1) + " with frequency " + str(v_freq_list[i]))
        self.log.drop('event_objects', axis=1, inplace=True)
        return variants, v_freq_list
