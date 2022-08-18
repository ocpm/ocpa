from typing import Dict, List, Any
import pandas as pd
from pandas import to_datetime
from datetime import datetime
import itertools
from collections import OrderedDict

from ocpa.objects.log.variants.obj import Event, Obj, ObjectCentricEventLog, MetaObjectCentricData, RawObjectCentricData


def add_event(events: Dict[str, Event], index, row, cfg) -> None:
    #print(cfg["val_names"])
    events[str(index)] = Event(
        id=str(index),
        act=row[cfg["act_name"]],
        time=to_datetime(row[cfg["time_name"]]),
        omap=list(itertools.chain.from_iterable(
            [row[obj]
             for obj in cfg["obj_names"] if (row[obj] != '{}' and row[obj] != [] and row[obj] != '[]' and row[obj] != '' and str(row[obj]).lower() != "nan")]
        )),
        vmap={attr: row[attr] for attr in cfg["val_names"]})

    # add start time if exists, otherwise None for performance analysis
    if "start_timestamp" in cfg:
        events[str(index)].vmap["start_timestamp"] = to_datetime(
            row[cfg["start_timestamp"]])
    else:
        events[str(index)].vmap["start_timestamp"] = None


def safe_split(row_obj):
    try:
        if '{' in row_obj or '[' in row_obj:
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
                    [[obj_id + '/' + str(obj) for i, obj_id in enumerate(row[obj])]
                     for obj in parameters["obj_names"] if row[obj] != '{}' and row[obj] != [] and row[obj] != '[]' and row[obj] != '' and str(row[obj]).lower() != "nan"]
                ))
                )
        acts.add(row[parameters["act_name"]])

    events = OrderedDict(sorted(events.items(), key=lambda kv: kv[1].time))

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


def name_type(typ: str) -> str:
    if typ == 'object':
        return 'string'
    else:
        return typ
