import time
from dataclasses import dataclass, field
from typing import List, Dict, Set, Any, Optional, Union, Tuple
from datetime import datetime
import networkx as nx
import itertools
import random
import numpy as np
import matplotlib.pyplot as plt
import networkx.algorithms.isomorphism as iso
from ocpa.objects.log.util.param import CsvParseParameters, JsonParseParameters


@dataclass
class Event:
    id: str
    act: str
    time: datetime
    omap: List[str]
    vmap: Dict[str, Any]
    # Kept for backward compatibility with the evaluation
    # corr: bool = field(default_factory=lambda: False)

    def __hash__(self):
        # keep the ID for now in places
        return id(self)

    def __repr__(self):
        return str(self.act) + str(self.time) + str(self.omap) + str(self.vmap)


@dataclass
class Obj:
    id: str
    type: str
    ovmap: Dict


# @dataclass
# class ObjectCentricEventLog:
#     events: List[Event]
#     objects: List[Obj]

#     # acts: List[str]  # AN
#     attr_names: List[str]  # AN
#     obj_types: List[str]  # OT
#     attr_types: field(default_factory=list)  # AT
#     attr_typ: field(default_factory=dict)  # pi_typ

#     act_attr: Dict[str, List[str]]  # allowed attr per act
#     # act_obj: Dict[str, List[str]]  # allowed ot per act

#     acts: Set[str] = field(init=False)  # TODO: change to list for json
#     # ress: Set[str] = field(init=False)  # TODO: change to list for json
#     # locs: Set[str] = field(init=False)  # TODO: change to list for json
#     # Used for OCEL json data to simplify UI on homepage
#     attr_events: List[str] = field(default_factory=lambda: [])

#     def __post_init__(self):
#         self.acts = {act for act in self.act_attr}


@dataclass
class MetaObjectCentricData:
    attr_names: List[str]  # AN
    attr_types: List[str]  # AT
    attr_typ: Dict  # pi_typ

    obj_types: List[str]  # OT

    act_attr: Dict[str, List[str]]  # allowed attr per act
    # act_obj: Dict[str, List[str]]  # allowed ot per act

    # acts: Set[str] = field(init=False)  # TODO: change to list for json
    # Used for OCEL json data to simplify UI on homepage
    attr_events: List[str] = field(default_factory=lambda: [])

    # def __post_init__(self):
    #     self.acts = {act for act in self.act_attr}


@dataclass
class RawObjectCentricData:
    events: Dict[str, Event]
    objects: Dict[str, Obj]

    @property
    def obj_ids(self) -> List[str]:
        return list(self.objects.keys())


@dataclass
class ObjectCentricEventLog:
    meta: MetaObjectCentricData
    raw: RawObjectCentricData

    def __post_init__(self):
        self.meta.locs = {}


class OCEL():
    def __init__(self, log, object_types=None, precalc=False, execution_extraction="weakly", leading_object_type="order", variant_extraction="complex", variant_timeout=3600):
        self._log = log
        self._log["event_index"] = self._log["event_id"]
        self._log = self._log.set_index("event_index")
        #self._event_mapping =  dict(zip(ocel["event_id"], ocel["event_objects"]))
        self._execution_extraction = execution_extraction
        self._leading_type = leading_object_type
        self._variant_extraction = variant_extraction
        self._variant_timeout = variant_timeout
        if object_types != None:
            self._object_types = object_types
        else:

            self._object_types = [
                c for c in self._log.columns if not c.startswith("event_")]
        # clean empty events
        self.clean_empty_events()
        self.create_efficiency_objects()
        #self._log = self._log[self._log.apply(lambda x: any([len(x[ot]) > 0 for ot in self._object_types]))]
        if precalc:
            self._eog = self.eog_from_log()
            self._cases, self._case_objects = self.calculate_cases()
            self._variants, self._variant_frequency, self._variant_graphs, self._variants_dict = self.calculate_variants()
        else:
            self._eog = None
            self._cases = None
            self._case_objects = None
            self._variants = None
            self._variant_graphs = None
            self._variant_frequency = None
            self._variants_dict = None

    def _get_log(self):
        return self._log

    def _set_log(self, log):
        self._log = log

    def _get_eog(self):
        if self._eog == None:
            self._eog = self.eog_from_log()
        return self._eog

    def _get_case_objects(self):
        if self._case_objects == None:
            self._cases, self._case_objects = self.calculate_cases()
        return self._case_objects

    def _get_cases(self):
        if self._cases == None:
            self._cases, self._case_objects = self.calculate_cases()
        return self._cases

    def _get_variants(self):
        if self._variants == None:
            self._variants, self._variant_frequency, self._variant_graphs, self._variants_dict = self.calculate_variants()
        return self._variants

    def _get_variant_frequency(self):
        if self._variant_frequency == None:
            self._variants, self._variant_frequency, self._variant_graphs, self._variants_dict = self.calculate_variants()
        return self._variant_frequency

    def _get_variant_graphs(self):
        if self._variant_graphs == None:
            self._variants, self._variant_frequency, self._variant_graphs, self._variants_dict = self.calculate_variants()
        return self._variant_graphs

    def _get_object_types(self):
        return self._object_types

    def _set_object_types(self, object_types):
        self._object_types = object_types

    def _get_variant_timeout(self):
        return self._variant_timeout

    def _set_variant_timeout(self, variant_timeout):
        self._variant_timeout = variant_timeout

    def _get_variants_dict(self):
        if self._variants_dict == None:
            self._variants, self._variant_frequency, self._variant_graphs, self._variants_dict = self.calculate_variants()
        return self._variants_dict

    log = property(_get_log, _set_log)
    object_types = property(_get_object_types, _set_object_types)
    eog = property(_get_eog)
    cases = property(_get_cases)
    case_objects = property(_get_case_objects)
    variants = property(_get_variants)
    variant_frequency = property(_get_variant_frequency)
    variant_graphs = property(_get_variant_graphs)
    variants_dict = property(_get_variants_dict)
    variant_timeout = property(_get_variant_timeout, _set_variant_timeout)

    def create_efficiency_objects(self):
        self._numpy_log = self._log.to_numpy()
        self._column_mapping = {k: v for v, k in enumerate(
            list(self._log.columns.values))}
        self._mapping = {c: dict(
            zip(self._log["event_id"], self._log[c])) for c in self._log.columns.values}

    def get_value(self, e_id, attribute):
        return self._mapping[attribute][e_id]

    def eog_from_log(self):
        ocel = self.log.copy()
        EOG = nx.DiGraph()
        EOG.add_nodes_from(ocel["event_id"].to_list())
        edge_list = []

        ot_index = {ot: list(ocel.columns.values).index(ot)
                    for ot in self.object_types}
        event_index = list(ocel.columns.values).index("event_id")
        arr = ocel.to_numpy()
        last_ev = {}
        for i in range(0, len(arr)):
            for ot in self.object_types:
                for o in arr[i][ot_index[ot]]:
                    if (ot, o) in last_ev.keys():
                        edge_source = arr[last_ev[(ot, o)]][event_index]
                        edge_target = arr[i][event_index]
                        edge_list += [(edge_source, edge_target)]
                    last_ev[(ot, o)] = i
        EOG.add_edges_from(edge_list)
        return EOG

    def calculate_cases(self):
        if self._execution_extraction == "weakly":
            ocel = self.log.copy()
            ocel["event_objects"] = ocel.apply(lambda x: set([(ot, o) for ot in self.object_types for o in x[ot]]),
                                               axis=1)
            # Add the possibility to remove edges
            cases = sorted(nx.weakly_connected_components(
                self.eog), key=len, reverse=True)
            obs = []
            mapping_objects = dict(
                zip(ocel["event_id"], ocel["event_objects"]))
            object_index = list(ocel.columns.values).index("event_objects")
            for case in cases:
                case_obs = []
                for event in case:
                    for ob in mapping_objects[event]:
                        case_obs += [ob]
                obs.append(list(set(case_obs)))
            ocel.drop('event_objects', axis=1, inplace=True)
            return cases, obs
        elif self._execution_extraction == "leading":
            ocel = self.log.copy()
            ocel["event_objects"] = ocel.apply(lambda x: set([(ot, o) for ot in self.object_types for o in x[ot]]),
                                               axis=1)
            OG = nx.Graph()
            OG.add_nodes_from(ocel["event_objects"].explode(
                "event_objects").to_list())
            #ot_index = {ot: list(ocel.values).index(ot) for ot in self.object_types}
            object_index = list(ocel.columns.values).index("event_objects")
            id_index = list(ocel.columns.values).index("event_id")
            edge_list = []
            cases = []
            obs = []
            # build object graph
            arr = ocel.to_numpy()
            for i in range(0, len(arr)):
                edge_list += list(itertools.combinations(
                    arr[i][object_index], 2))
            edge_list = [x for x in edge_list if x]
            OG.add_edges_from(edge_list)
            # construct a mapping for each object
            object_event_mapping = {}
            for i in range(0, len(arr)):
                for ob in arr[i][object_index]:
                    if ob not in object_event_mapping.keys():
                        object_event_mapping[ob] = []
                    object_event_mapping[ob].append(arr[i][id_index])

            # for each leading object extract the case
            # self.object_types[0] # leading_type
            leading_type = self._leading_type
            for node in OG.nodes:
                case = []
                if node[0] != leading_type:
                    continue
                relevant_objects = []
                ot_mapping = {}
                o_mapping = {}
                ot_mapping[leading_type] = 0
                next_level_objects = OG.neighbors(node)
                #relevant_objects += next_level_objects
                for level in range(1, len(self.object_types)):
                    to_be_next_level = []
                    for (ot, o) in next_level_objects:
                        if ot not in ot_mapping.keys():
                            ot_mapping[ot] = level
                        else:
                            if ot_mapping[ot] != level:
                                continue
                        relevant_objects.append((ot, o))
                        o_mapping[(ot, o)] = level
                        to_be_next_level += OG.neighbors((ot, o))
                    next_level_objects = to_be_next_level

                relevant_objects = set(relevant_objects)
                # add all leading events, and all events where only relevant objects are included
                obs_case = relevant_objects.union(set([node]))
                events_to_add = []
                for ob in obs_case:
                    events_to_add += object_event_mapping[ob]
                events_to_add = list(set(events_to_add))
                case = events_to_add
                cases.append(case)
                obs.append(list(obs_case))
            ocel.drop('event_objects', axis=1, inplace=True)
            return cases, obs

    def _project_subgraph_on_activity(self, v_g, case_id, mapping_objects, mapping_activity):
        v_g_ = v_g.copy()
        for node in v_g.nodes():
            if not set(mapping_objects[node]) & set(self.case_objects[case_id]):
                v_g_.remove_node(node)
                continue
            v_g_.nodes[node]['label'] = mapping_activity[node] + ": ".join(
                [e[0] for e in sorted(list(set(mapping_objects[node]) & set(self.case_objects[case_id])))])
        for edge in v_g.edges():
            source, target = edge
            if not set(mapping_objects[source]) & set(mapping_objects[target]) & set(self.case_objects[case_id]):
                v_g_.remove_edge(source, target)
                continue
            v_g_.edges[edge]['type'] = ": ".join(
                [e[0] for e in sorted(list(set(mapping_objects[source]).intersection(set(mapping_objects[target])) & set(self.case_objects[case_id])))])
            v_g_.edges[edge]['label'] = ": ".join(
                [str(e) for e in sorted(list(set(mapping_objects[source]).intersection(set(mapping_objects[target])) & set(self.case_objects[case_id])))])
        return v_g_

    def calculate_variants(self):
        if self._variant_extraction == "complex":
            return self.calculate_variants_complex()
        else:
            return self.calculate_variants_naive()

    def calculate_variants_complex(self):
        timeout = self._variant_timeout
        variants = None
        self.log["event_objects"] = self.log.apply(
            lambda x: [(ot, o) for ot in self.object_types for o in x[ot]], axis=1)
        variants_dict = dict()
        variants_graph_dict = dict()
        variant_graphs = dict()
        case_id = 0
        mapping_activity = dict(
            zip(self.log["event_id"], self.log["event_activity"]))
        mapping_objects = dict(
            zip(self.log["event_id"], self.log["event_objects"]))
        start_timestamp = time.time()
        for v_g in self.cases:

            case = self._project_subgraph_on_activity(self.eog.subgraph(
                v_g), case_id, mapping_objects, mapping_activity)

            variant = nx.weisfeiler_lehman_graph_hash(
                case, node_attr="label", edge_attr="type")
            #variant = e_string
            # print(e_string)
            variant_string = variant
            if variant_string not in variants_dict:
                variants_dict[variant_string] = []
                variants_graph_dict[variant_string] = []
                variant_graphs[variant_string] = (
                    case, self.case_objects[case_id])  # EOG.subgraph(v_g)#case
            variants_dict[variant_string].append(case_id)
            variants_graph_dict[variant_string].append(case)
            case_id += 1
        #print("Before refining: "+str(len(variants_dict.keys()))+" equivalence classes")
        #print("Time taken for first step "+str(time.time()-start_timestamp))

        start_timestamp = time.time()
        # refine the classes
        # for _class in variants_graph_dict.keys():
        #     subclass_counter = 0
        #     subclass_mappings = {}
        #
        #     for j in range(0,len(variants_graph_dict[_class])):
        #         exec = variants_graph_dict[_class][j]
        #         case_id = variants_dict[_class][j]
        #         found = False
        #         for i in range(1,subclass_counter+1):
        #             if nx.is_isomorphic(exec,subclass_mappings[i][0][0], node_match = lambda x,y: x['label'] == y['label'], edge_match = lambda x,y: x['type'] == y['type']):
        #                 subclass_mappings[subclass_counter].append((exec,case_id))
        #                 found = True
        #                 break
        #         if found:
        #             continue
        #         subclass_counter +=1
        #         subclass_mappings[subclass_counter] = [(exec,case_id)]
        #         if (time.time() - start_timestamp) > timeout:
        #             raise Exception("timeout")
        #     for ind in subclass_mappings.keys():
        #         variants_dict[_class+str(ind)] = [case_id for (exec, case_id) in subclass_mappings[ind]]
        #         (exec, case_id) = subclass_mappings[ind][0]
        #         variant_graphs[_class+str(ind)] = (exec, self.case_objects[case_id])
        #     del variants_dict[_class]
        #     del variant_graphs[_class]
        # print("After refining: "+str(len(variants_dict.keys()))+" equivalence classes")
        # print("Time taken for second step: "+str(time.time() - start_timestamp))

        variant_frequencies = {
            v: len(variants_dict[v]) / len(self.cases) for v in variants_dict.keys()}
        variants, v_freq_list = map(list,
                                    zip(*sorted(list(variant_frequencies.items()), key=lambda x: x[1], reverse=True)))
        variant_event_map = {}
        for v_id in range(0, len(variants)):
            v = variants[v_id]
            cases = [self.cases[c_id] for c_id in variants_dict[v]]
            events = set().union(*cases)
            for e in events:
                if e not in variant_event_map.keys():
                    variant_event_map[e] = []
                variant_event_map[e] += [v_id]
        self.log["event_variant"] = self.log["event_id"].map(variant_event_map)
        #self.log["event_variant"] = self.log["event_variant"].astype(int)
        # for i in range(0, 10):
        #    print("Class number " + str(i + 1) + " with frequency " + str(v_freq_list[i]))
        self.log.drop('event_objects', axis=1, inplace=True)
        return variants, v_freq_list, variant_graphs, variants_dict

    def calculate_variants_naive(self):
        timeout = self._variant_timeout
        variants = None
        self.log["event_objects"] = self.log.apply(lambda x: [(ot, o) for ot in self.object_types for o in x[ot]],
                                                   axis=1)
        variants_dict = dict()
        variants_graph_dict = dict()
        variant_graphs = dict()
        case_id = 0
        mapping_activity = dict(
            zip(self.log["event_id"], self.log["event_activity"]))
        mapping_objects = dict(
            zip(self.log["event_id"], self.log["event_objects"]))
        start_timestamp = time.time()
        for v_g in self.cases:

            case = self._project_subgraph_on_activity(self.eog.subgraph(
                v_g), case_id, mapping_objects, mapping_activity)
            variant = "ArbitraryVariantString"
            variant_string = variant
            if variant_string not in variants_dict:
                variants_dict[variant_string] = []
                variants_graph_dict[variant_string] = []
                variant_graphs[variant_string] = (
                    case, self.case_objects[case_id])  # EOG.subgraph(v_g)#case
            variants_dict[variant_string].append(case_id)
            variants_graph_dict[variant_string].append(case)
            case_id += 1
        print("Before refining: " +
              str(len(variants_dict.keys())) + " equivalence classes")
        print("Time taken for first step " +
              str(time.time() - start_timestamp))
        start_timestamp = time.time()
        # refine the classes
        for _class in variants_graph_dict.keys():
            subclass_counter = 0
            subclass_mappings = {}

            for j in range(0, len(variants_graph_dict[_class])):
                exec = variants_graph_dict[_class][j]
                case_id = variants_dict[_class][j]
                found = False
                for i in range(1, subclass_counter + 1):
                    if nx.faster_could_be_isomorphic(exec, subclass_mappings[i][0][0]):
                        if nx.is_isomorphic(exec, subclass_mappings[i][0][0], node_match=lambda x, y: x['label'] == y['label'], edge_match=lambda x, y: x['type'] == y['type']):
                            subclass_mappings[subclass_counter].append(
                                (exec, case_id))
                            found = True
                            break
                if found:
                    continue
                subclass_counter += 1
                subclass_mappings[subclass_counter] = [(exec, case_id)]
                if (time.time() - start_timestamp) > timeout:
                    raise Exception("timeout")
            for ind in subclass_mappings.keys():
                variants_dict[_class + str(ind)] = [case_id for (exec,
                                                                 case_id) in subclass_mappings[ind]]
                (exec, case_id) = subclass_mappings[ind][0]
                variant_graphs[_class +
                               str(ind)] = (exec, self.case_objects[case_id])
            del variants_dict[_class]
            del variant_graphs[_class]
        print("After refining: " + str(len(variants_dict.keys())) +
              " equivalence classes")
        print("Time taken for second step: " +
              str(time.time() - start_timestamp))

        variant_frequencies = {
            v: len(variants_dict[v]) / len(self.cases) for v in variants_dict.keys()}
        variants, v_freq_list = map(list,
                                    zip(*sorted(list(variant_frequencies.items()), key=lambda x: x[1], reverse=True)))
        variant_event_map = {}
        for v_id in range(0, len(variants)):
            v = variants[v_id]
            cases = [self.cases[c_id] for c_id in variants_dict[v]]
            events = set().union(*cases)
            for e in events:
                if e not in variant_event_map.keys():
                    variant_event_map[e] = []
                variant_event_map[e] += [v_id]
        self.log["event_variant"] = self.log["event_id"].map(variant_event_map)
        # self.log["event_variant"] = self.log["event_variant"].astype(int)
        # for i in range(0, 10):
        #    print("Class number " + str(i + 1) + " with frequency " + str(v_freq_list[i]))
        self.log.drop('event_objects', axis=1, inplace=True)
        return variants, v_freq_list, variant_graphs, variants_dict

    def get_objects_of_variants(self, variants):
        obs = {}
        for ot in self.object_types:
            obs[ot] = set()
        for v_id in variants:
            for case_id in self.variants_dict[self.variants[v_id]]:
                for ob in self.case_objects[case_id]:
                    obs[ob[0]].add(ob[1])

        return obs

    def remove_object_references(self, to_keep):
        # this is in place!
        for ot in self.object_types:
            self.log[ot] = self.log[ot].apply(
                lambda x: list(set(x) & to_keep[ot]))
        self.clean_empty_events()

    def clean_empty_events(self):
        self._log = self._log[self._log[self._object_types].astype(
            bool).any(axis=1)]

    def sample_cases(self, percent):
        index_array = random.sample(
            list(range(0, len(self.cases))), int(len(self.cases)*percent))
        self._cases = [self.cases[i] for i in index_array]
        self._case_objects = [self.case_objects[i] for i in index_array]

    def copy(self):
        return OCEL(self.log.copy(), object_types=self.object_types, execution_extraction=self._execution_extraction, leading_object_type=self._leading_type, variant_extraction=self._variant_extraction, variant_timeout=self.variant_timeout)
