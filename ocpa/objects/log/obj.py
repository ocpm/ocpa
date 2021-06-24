from dataclasses import dataclass, field
from typing import List, Dict, Set, Any, Optional, Union, Tuple
from datetime import datetime


from ocpa.objects.log.util.param import CsvParseParameters, JsonParseParameters


@dataclass
class EventId:
    id: str


@dataclass
class EventClassic(EventId):
    act: str
    time: datetime


@dataclass
class EventClassicResource(EventClassic):
    vmap: Dict[str, Any]


@dataclass
class Event(EventClassic):
    omap: List[str]
    vmap: Dict[str, Any]
    # Kept for backward compatibility with the evaluation
    corr: bool = field(default_factory=lambda: False)


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
    ress: Set[str] = field(init=False)  # TODO: change to list for json
    locs: Set[str] = field(init=False)  # TODO: change to list for json
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
class ObjectCentricData:
    meta: MetaObjectCentricData
    raw: RawObjectCentricData
    vmap_param: Union[CsvParseParameters, JsonParseParameters]

    def __post_init__(self):
        self.meta.locs = {}


def sort_events(data: ObjectCentricData) -> None:
    events = data.raw.events
    data.raw.events = {k: event for k, event in sorted(
        events.items(), key=lambda item: item[1].time)}
