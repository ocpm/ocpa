from typing import Dict, List, Any
import pandas as pd
from pandas import to_datetime
from ocpa.objects.log.variants.obj import Event, Obj, ObjectCentricEventLog, MetaObjectCentricData, RawObjectCentricData


def apply(df: pd.DataFrame) -> ObjectCentricEventLog:
    events = {}
    objects = {}
    acts = set()
    obj_names = set([x for x in df.columns if not x.startswith("event_")])
    val_names = set([x for x in df.columns if x.startswith(
        "event_")]) - set(['event_activity', 'event_timestamp', 'event_start_timestamp'])
    for index, row in df.iterrows():
        add_event(events, index, row, obj_names, val_names)
        add_obj(objects, [(o, obj) for obj in obj_names for o in row[obj]])
        acts.add(row['event_activity'])

    attr_typ = {attr: name_type(str(df.dtypes[attr]))
                for attr in val_names}
    attr_types = list(set(typ for typ in attr_typ.values()))
    act_attr = {act: val_names for act in acts}
    meta = MetaObjectCentricData(
        attr_names=val_names,
        attr_types=attr_types,
        attr_typ=attr_typ,
        obj_types=obj_names,
        act_attr=act_attr
    )
    raw = RawObjectCentricData(
        events=events,
        objects=objects
    )
    return ObjectCentricEventLog(meta, raw)


def add_event(events: Dict[str, Event], index, row, obj_names, val_names) -> None:
    events[str(index)] = Event(
        id=str(index),
        act=row['event_activity'],
        time=to_datetime(row['event_timestamp']),
        omap=[o for obj in obj_names for o in row[obj]],
        vmap={attr: row[attr] for attr in val_names})
    # add start time if exists, otherwise None for performance analysis
    if "event_start_timestamp" in val_names:
        events[str(index)].vmap["start_timestamp"] = to_datetime(
            row['event_start_timestamp'])
    else:
        events[str(index)].vmap["start_timestamp"] = to_datetime(
            row['event_timestamp'])


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
        obj_id = obj_id_typ[0]  # First entry is the id
        obj_typ = obj_id_typ[1]  # second entry is the object type
        if obj_id not in objects:
            objects[obj_id] = Obj(id=obj_id, type=obj_typ, ovmap={})


def name_type(typ: str) -> str:
    if typ == 'object':
        return 'string'
    else:
        return typ
