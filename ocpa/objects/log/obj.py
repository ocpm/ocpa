from dataclasses import dataclass, field
from typing import List, Dict, Set, Any, Optional, Union, Tuple
from datetime import datetime
import networkx as nx

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


@dataclass
class MetaObjectCentricData:
    attr_names: List[str]  # AN
    attr_types: List[str]  # AT
    attr_typ: Dict  # pi_typ

    obj_types: List[str]  # OT

    act_attr: Dict[str, List[str]]  # allowed attr per act
    # act_obj: Dict[str, List[str]]  # allowed ot per act

    acts: Set[str] = field(init=False)  # TODO: change to list for json
    # Used for OCEL json data to simplify UI on homepage
    attr_events: List[str] = field(default_factory=lambda: [])

    def __post_init__(self):
        self.acts = {act for act in self.act_attr}


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
    def __init__(self, log, object_types=None, precalc=False):
        self._log = log
        if object_types != None:
            self._object_types = object_types
        else:

            self._object_types = [c for c in self._log.columns if not c.startswith("event_")]
        #clean empty events
        self._log = self._log[self._log[self._object_types].astype(bool).any(axis=1)]
        #self._log = self._log[self._log.apply(lambda x: any([len(x[ot]) > 0 for ot in self._object_types]))]
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
        edge_list = []

        ot_index = {ot: list(ocel.columns.values).index(ot) for ot in self.object_types}
        event_index = list(ocel.columns.values).index("event_id")
        arr = ocel.to_numpy()
        last_ev = {}
        for i in range(0,len(arr)):
            for ot in self.object_types:
                for o in arr[i][ot_index[ot]]:
                    if (ot,o) in last_ev.keys():
                        edge_source = arr[last_ev[(ot,o)]][event_index]
                        edge_target = arr[i][event_index]
                        edge_list += [(edge_source,edge_target)]
                    last_ev[(ot,o)] = i
        EOG.add_edges_from(edge_list)
        return EOG

    def calculate_cases(self):
        # Add the possibility to remove edges
        cases = sorted(nx.weakly_connected_components(self.eog), key=len , reverse=True)
        return cases

    def _project_subgraph_on_activity(self, v_g,mapping_objects,mapping_activity):
        for node in v_g.nodes():
            v_g.nodes[node]['label'] = mapping_activity[node]
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
        mapping_activity = dict(zip(self.log["event_id"], self.log["event_activity"]))
        mapping_objects = dict(zip(self.log["event_id"], self.log["event_objects"]))
        for v_g in self.cases:
            case = self._project_subgraph_on_activity(self.eog.subgraph(v_g),mapping_objects,mapping_activity)
            variant = nx.weisfeiler_lehman_graph_hash(case, node_attr="label",
                                                      edge_attr="type")
            variant_string = variant
            if variant_string not in variants_dict:
                variants_dict[variant_string] = []
                variant_graphs[variant_string] = case  # EOG.subgraph(v_g)#case
            variants_dict[variant_string].append(case_id)
            case_id += 1
        variant_frequencies = {v: len(variants_dict[v]) / len(self.cases) for v in variants_dict.keys()}
        variants, v_freq_list = map(list,
                                    zip(*sorted(list(variant_frequencies.items()), key=lambda x: x[1], reverse=True)))
        variant_event_map = {}
        for v_id in range(0, len(variants)):
            v = variants[v_id]
            cases = [self.cases[c_id] for c_id in variants_dict[v]]
            events = set().union(*cases)
            for e in events:
                variant_event_map[e] = v_id
        self.log["event_variant"] = self.log["event_id"].map(variant_event_map)
        self.log["event_variant"] = self.log["event_variant"].astype(int)
        #for i in range(0, 10):
        #    print("Class number " + str(i + 1) + " with frequency " + str(v_freq_list[i]))
        self.log.drop('event_objects', axis=1, inplace=True)
        return variants, v_freq_list

