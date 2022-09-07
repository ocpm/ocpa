from typing import Dict, List, Any
import pandas as pd
from pandas import to_datetime
import itertools
from ocpa.objects.log.variants.obj import Event, Obj, ObjectCentricEventLog, MetaObjectCentricData, RawObjectCentricData


def apply(df: pd.DataFrame, parameters: Dict) -> ObjectCentricEventLog:
    if parameters is None:
        raise ValueError("Specify parsing parameters")
    events = {}
    objects = {}
    acts = set()
    for index, row in df.iterrows():
        add_event(events, index, row, parameters)
        add_obj(objects,
                # Only nonempty sets of objects ids per object type
                list(itertools.chain.from_iterable(
                    [[obj_id + '/' + str(obj) for i, obj_id in enumerate(safe_split(row[obj]))]
                     for obj in parameters["obj_names"] if row[obj] != '{}' and str(row[obj]).lower() != "nan"]
                ))
                )
        acts.add(row[parameters["act_name"]])

    attr_typ = {attr: name_type(str(df.dtypes[attr]))
                for attr in parameters["val_names"]}
    attr_types = list(set(typ for typ in attr_typ.values()))
    act_attr = {act: parameters["val_names"] for act in acts}
    meta = MetaObjectCentricData(
        attr_names=parameters["val_names"],
        attr_types=attr_types,
        attr_typ=attr_typ,
        obj_types=parameters["obj_names"],
        act_attr=act_attr
    )
    raw = RawObjectCentricData(
        events=events,
        objects=objects
    )
    return ObjectCentricEventLog(meta, raw)


def add_event(events: Dict[str, Event], index, row, cfg) -> None:
    events[str(index)] = Event(
        id=str(index),
        act=row[cfg["act_name"]],
        time=to_datetime(row[cfg["time_name"]]),
        omap=list(itertools.chain.from_iterable(
            [safe_split(row[obj])
             for obj in cfg["obj_names"] if (row[obj] != '{}' and str(row[obj]).lower() != "nan")]
        )),
        vmap={attr: row[attr] for attr in cfg["val_names"]})


def safe_split(row_obj):
    try:
        if '{' in row_obj:
            return [x.strip() for x in row_obj[1:-1].split(',')]
        else:
            return row_obj.split(',')
    except TypeError:
        return []  # f'NA-{next(counter)}'


def add_obj(objects: Dict[str, Obj], objs: List[str]) -> None:
    for obj_id_typ in objs:
        obj_id_typ = obj_id_typ.split('/')  # Unpack
        obj_id = obj_id_typ[0]  # First entry is the id
        obj_typ = obj_id_typ[1]  # second entry is the object type
        if obj_id not in objects:
            objects[obj_id] = Obj(id=obj_id, type=obj_typ, ovmap={})


def name_type(typ: str) -> str:
    if typ == 'object':
        return 'string'
    else:
        return typ


# def old_apply(df: pd.DataFrame, parameters=None) -> ObjectCentricEventLog:
#     # parses the given dict
#     events = parse_events(df)
#     objects = parse_objects(df)
#     # Uses the last found value type
#     attr_events = {v:
#                    str(type(events[eid].vmap[v])) for eid in events
#                    for v in events[eid].vmap}
#     attr_objects = {v:
#                     str(type(objects[oid].ovmap[v])) for oid in objects
#                     for v in objects[oid].ovmap
#                     }
#     attr_types = list({attr_events[v] for v in attr_events}.union(
#         {attr_objects[v] for v in attr_objects}))
#     attr_typ = {**attr_events, **attr_objects}
#     act_attr = {}
#     for eid, event in events.items():
#         act = event.act
#         if act not in act_attr:
#             act_attr[act] = {v for v in event.vmap}
#         else:
#             act_attr[act] = act_attr[act].union({v for v in event.vmap})
#     for act in act_attr:
#         act_attr[act] = list(act_attr[act])
#     meta = MetaObjectCentricData(attr_names=[],
#                                  obj_types=[],
#                                  attr_types=attr_types,
#                                  attr_typ=attr_typ,
#                                  act_attr=act_attr,
#                                  attr_events=list(attr_events.keys()))
#     data = ObjectCentricEventLog(
#         meta, RawObjectCentricData(events, objects))
#     return data


# def parse_events(df: pd.DataFrame) -> Dict[str, Event]:
#     events = {}
#     for i, row in df.iterrows():
#         eid = row['event_id']
#         act_name = row['event_activity']
#         time = row['event_timestamp']

#         eve_cols = [x for x in df.columns if not x.startswith("object_")]
#         obj_cols = [x for x in df.columns if x.startswith("object_")]
#         omap = [oi for ot in obj_cols for oi in row[ot]]
#         vmap = {}
#         for col in eve_cols:
#             if col not in ["event_activity", "event_id", "event_timestamp"]:
#                 vmap[col] = row[col]
#         events[eid] = Event(id=eid, act=act_name, omap=omap,
#                             vmap=vmap, time=time)
#     return events


# def parse_objects(df: pd.DataFrame) -> Dict[str, Obj]:
#     temp_objects = {}
#     obj_cols = [x for x in df.columns if not x.startswith("object_")]
#     for i, row in df.iterrows():
#         for ot in obj_cols:
#             for oi in row[ot]:
#                 if oi not in temp_objects:
#                     temp_objects[oi] = {}
#                     temp_objects[oi]["type"] = ot
#     objects = {temp_objects[obj]: Obj(id=temp_objects[obj],
#                                       type=temp_objects[obj]["type"],
#                                       ovmap={})
#                for obj in temp_objects}
#     return objects
