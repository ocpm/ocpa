from typing import Dict, List, Any
import pandas as pd
from datetime import datetime

from ocpa.objects.log.importer.ocel.parameters import JsonParseParameters
from ocpa.objects.log.obj import Event, Obj, ObjectCentricEventLog, MetaObjectCentricData, RawObjectCentricData


def apply(df: pd.DataFrame, parameters=None) -> ObjectCentricEventLog:
    # parses the given dict
    events = parse_events(df)
    objects = parse_objects(df)
    # Uses the last found value type
    attr_events = {v:
                   str(type(events[eid].vmap[v])) for eid in events
                   for v in events[eid].vmap}
    attr_objects = {v:
                    str(type(objects[oid].ovmap[v])) for oid in objects
                    for v in objects[oid].ovmap
                    }
    attr_types = list({attr_events[v] for v in attr_events}.union(
        {attr_objects[v] for v in attr_objects}))
    attr_typ = {**attr_events, **attr_objects}
    act_attr = {}
    for eid, event in events.items():
        act = event.act
        if act not in act_attr:
            act_attr[act] = {v for v in event.vmap}
        else:
            act_attr[act] = act_attr[act].union({v for v in event.vmap})
    for act in act_attr:
        act_attr[act] = list(act_attr[act])
    meta = MetaObjectCentricData(attr_names=[],
                                 obj_types=[],
                                 attr_types=attr_types,
                                 attr_typ=attr_typ,
                                 act_attr=act_attr,
                                 attr_events=list(attr_events.keys()))
    data = ObjectCentricEventLog(
        meta, RawObjectCentricData(events, objects))
    return data


def parse_events(df: pd.DataFrame) -> Dict[str, Event]:
    events = {}
    for i, row in df.iterrows():
        eid = row['event_id']
        act_name = row['event_activity']
        time = row['event_timestamp']

        eve_cols = [x for x in df.columns if not x.startswith("object_")]
        obj_cols = [x for x in df.columns if x.startswith("object_")]
        omap = [oi for ot in obj_cols for oi in row[ot]]
        vmap = {}
        for col in eve_cols:
            if col not in ["event_activity", "event_id", "event_timestamp"]:
                vmap[col] = row[col]
        events[eid] = Event(id=eid, act=act_name, omap=omap,
                            vmap=vmap, time=time)
    return events


def parse_objects(df: pd.DataFrame) -> Dict[str, Obj]:
    temp_objects = {}
    obj_cols = [x for x in df.columns if not x.startswith("object_")]
    for i, row in df.iterrows():
        for ot in obj_cols:
            for oi in row[ot]:
                if oi not in temp_objects:
                    temp_objects[oi] = {}
                    temp_objects[oi]["type"] = ot
    objects = {temp_objects[obj]: Obj(id=temp_objects[obj],
                                      type=temp_objects[obj]["type"],
                                      ovmap={})
               for obj in temp_objects}
    print(objects)
    return objects
