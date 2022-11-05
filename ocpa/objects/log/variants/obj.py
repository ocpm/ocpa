from dataclasses import dataclass, field
from typing import List, Dict, Set, Any
from datetime import datetime


@dataclass
class Event:
    id: str
    act: str
    time: datetime
    omap: List[str]
    vmap: Dict[str, Any]

    def __hash__(self):
        # keep the ID for now in places
        return id(self)

    def __repr__(self):
        return f'Event {self.id} - Activity: {self.act}, Timestamp: {str(self.time)}, OMAP: {str(self.omap)}, VMAP: {str(self.vmap)}'


@dataclass
class Obj:
    id: str
    type: str
    ovmap: Dict

    def __repr__(self):
        return f'Object {self.id} - Type: {self.type}, OVMAP: {str(self.ovmap)}'


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

    @property
    def activities(self) -> Set[str]:
        return set([self.raw.events[e].act for e in self.raw.events])

    def act_events(self, act: str) -> List[str]:
        return [e for e in self.raw.events if self.raw.events[e].act == act]

    @property
    def types(self) -> Set[str]:
        return set(self.meta.obj_types)

    def ot_objects(self, ot: str) -> List[str]:
        return [oid for oid in self.raw.objects if self.raw.objects[oid].type == ot]

    def obj_events(self, oid: str) -> List[str]:
        return [e for e in self.raw.events if oid in self.raw.events[e].omap]

    def eve_objects(self, eid: str) -> List[str]:
        return self.raw.events[eid].omap

    def sequence(self, oid: str) -> List[Event]:
        events = [self.raw.events[e] for e in self.obj_events(oid)]
        events.sort(key=lambda x: x.time)
        return events

    def trace(self, oid: str) -> List[str]:
        trace = [e.act for e in self.sequence(oid)]
        return trace

    def ot_events(self, ot: str) -> List[str]:
        events = []
        for e in self.raw.events:
            if any(ot == self.raw.objects[oid].type for oid in self.raw.events[e].omap):
                events.append(e)
        return events

    def ot_objects_of_an_event(self, eid: str, ot: str) -> List[str]:
        return [oid for oid in self.raw.events[eid].omap if self.raw.objects[oid].type == ot]

    def num_ot_objects_containing_acts(self, ot: str, acts: List[str]) -> int:
        objects = []
        for oid in self.ot_objects(ot):
            trace = self.trace(oid)
            if all(act in trace for act in acts):
                objects.append(oid)
        return len(objects)

        # return len([oid for oid in self.raw.objects if self.raw.objects[oid].type == ot and act in self.trace(oid)])

    def num_ot_objects_containing_act1_followed_by_act2(self, ot: str, act1: str, act2: str) -> int:
        objects = []
        for oid in self.ot_objects(ot):
            trace = self.trace(oid)
            if act1 in trace and act2 in trace:
                act1_idx = trace.index(act1)
                act2_idx = trace.index(act2)
                if act1_idx < act2_idx:
                    objects.append(oid)
        return len(objects)

    def num_events_relating_one_ot(self, ot: str, act: str) -> int:
        events = []
        for eid in self.act_events(act):
            if len([oid for oid in self.eve_objects(eid) if self.raw.objects[oid].type == ot]) == 1:
                events.append(eid)
        return len(events)

    def num_events_relating_no_ot(self, ot: str, act: str) -> int:
        events = []
        for eid in self.act_events(act):
            if len([oid for oid in self.eve_objects(eid) if self.raw.objects[oid].type == ot]) == 0:
                events.append(eid)
        return len(events)

    def num_events_relating_multiple_ot(self, ot: str, act: str) -> int:
        events = []
        for eid in self.act_events(act):
            if len([oid for oid in self.eve_objects(eid) if self.raw.objects[oid].type == ot]) > 1:
                events.append(eid)
        return len(events)

    def causal_relation(self, ot: str, act1: str, act2: str):
        num_acts = self.num_ot_objects_containing_acts(ot, [act1, act2])
        if num_acts > 0:
            return self.num_ot_objects_containing_act1_followed_by_act2(ot, act1, act2)/num_acts
        else:
            return 0

    # not tested yet
    def concur_relation(self, ot: str, act1: str, act2: str):
        num_act1_follwed_by_act2 = self.num_ot_objects_containing_act1_followed_by_act2(
            ot, act1, act2)
        num_act2_follwed_by_act1 = self.num_ot_objects_containing_act1_followed_by_act2(
            ot, act2, act1)
        sum_num = num_act1_follwed_by_act2+num_act2_follwed_by_act1
        if sum_num > 0:
            temp_list = [num_act1_follwed_by_act2, num_act2_follwed_by_act1]
            return 1 - ((max(temp_list)-min(temp_list))/sum_num)
        else:
            return 0

    def choice_relation(self, ot: str, act1: str, act2: str):
        num_act1 = self.num_ot_objects_containing_acts(
            ot, [act1])
        num_act2 = self.num_ot_objects_containing_acts(
            ot, [act2])
        sum_num = num_act1+num_act2
        print(num_act1, num_act2, sum_num)
        if sum_num > 0:
            num_act1_and_act2 = self.num_ot_objects_containing_acts(
                ot, [act1, act2])
            return 1 - (num_act1_and_act2+num_act1_and_act2)/sum_num
        else:
            return 0

    def absent_involvement(self, ot: str, act: str):
        if len(self.act_events(act)) == 0:
            return 0
        return self.num_events_relating_no_ot(ot, act)/len(self.act_events(act))

    def singular_involvement(self, ot: str, act: str):
        if len(self.act_events(act)) == 0:
            return 0
        return self.num_events_relating_one_ot(ot, act)/len(self.act_events(act))

    def multiple_involvement(self, ot: str, act: str):
        if len(self.act_events(act)) == 0:
            return 0
        return self.num_events_relating_multiple_ot(ot, act)/len(self.act_events(act))
