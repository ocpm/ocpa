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
    def __init__(self, log, object_types=None, precalc=False):
        self._log = log
        if object_types != None:
            self._object_types = object_types
        else:
            self._object_types = [
                c for c in self._log.columns if not c.startswith("event_")]
        if precalc:
            self._eog = self.eog_from_log()
        else:
            self._eog = None

    def _get_log(self):
        return self._log

    def _set_log(self, log):
        self._log = log

    def _get_eog(self):
        if self._eog == None:
            self._eog = self.eog_from_log()
        return self._eog

    def _get_object_types(self):
        return self._object_types

    def _set_object_types(self, object_types):
        self.object_types = object_types

    log = property(_get_log, _set_log)
    object_types = property(_get_object_types, _set_object_types)
    eog = property(_get_eog)

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
