import logging
import random
from typing import Any

import pandas as pd
from ocpa.objects.log.variants.obj import (
    Event,
    MetaObjectCentricData,
    Obj,
    ObjectCentricEventLog,
    RawObjectCentricData,
)


def _sample_dict(n: int, dy: dict, seed: int = 42) -> dict:
    """only exists for logging purposes"""
    random.seed(seed)
    keys = random.sample(list(dy.keys()), n)
    return {k: dy[k] for k in keys}


def apply(df: pd.DataFrame, parameters: dict = None) -> ObjectCentricEventLog:
    obj_df = pd.DataFrame({"object_id": []})
    if "objects_table" in parameters:
        obj_df = parameters["objects_table"]

    events = {}
    objects = {}
    acts = set()
    obj_names = set([x for x in df.columns if not x.startswith("event_")])
    val_names = set([x for x in df.columns if x.startswith("event_")]) - set(
        ["event_activity", "event_timestamp", "event_start_timestamp"]
    )
    obj_event_mapping = {}

    for index, row in enumerate(df.itertuples(), 1):
        add_event(events, index, row, obj_names, val_names)
        objs = [
            (oid, ot) for ot in obj_names for oid in getattr(row, ot)
        ]  # maybe it should be getattr(row, oid)... do test!
        add_obj(
            objects=objects,
            index=index,
            objs=objs,
            obj_event_mapping=obj_event_mapping,
        )
        acts.add(getattr(row, "event_activity"))
    attr_typ = {attr: name_type(str(df.dtypes[attr])) for attr in val_names}
    attr_types = list(set(typ for typ in attr_typ.values()))
    act_attr = {act: val_names for act in acts}
    meta = MetaObjectCentricData(
        attr_names=val_names,
        attr_types=attr_types,
        attr_typ=attr_typ,
        obj_types=obj_names,
        act_attr=act_attr,
    )
    objects = add_obj_attributes(objects=objects, objects_table=obj_df)
    logging.debug("*" * 128)
    logging.debug(type(objects))
    logging.debug(_sample_dict(5, objects))
    raw = RawObjectCentricData(
        events=events, objects=objects, obj_event_mapping=obj_event_mapping
    )
    return ObjectCentricEventLog(meta, raw)


def df_to_objs_dict(objects_df: pd.DataFrame) -> dict[str, Obj]:
    # helper function for vectorized add_obj_attributes function (concept)
    pass


def add_obj_attributes(
    objects: dict[str, Obj], objects_table: pd.DataFrame
) -> dict[str, Obj]:
    # select only rows from objects table that occur in the OCEL
    objects_table = objects_table.loc[objects_table["object_id"].isin(objects.keys())]
    # """
    # in vectorized manner or via apply or via set_index().to_dict() (with multi index maybe):
    # instantiate dict/set of Obj at once
    # """

    for i, oid in enumerate(objects):
        # obj_attrs is a pd.DataFrame (with objects and their attributes) filtered on object id
        obj_attrs = objects_table.loc[objects_table["object_id"] == oid]
        if not obj_attrs.empty:
            objects[oid].ovmap = obj_attrs.iloc[0, 1:].to_dict()

    return objects


def add_event(
    events: dict[str, Event], index: int, row, obj_names: set[str], val_names: set[str]
) -> None:
    events[str(index)] = Event(
        id=str(index),
        act=getattr(row, "event_activity"),
        time=pd.to_datetime(getattr(row, "event_timestamp")),
        omap=[o for obj in obj_names for o in getattr(row, obj)],
        vmap={attr: getattr(row, attr) for attr in val_names},
    )
    # add start time if exists, otherwise None for performance analysis
    if "event_start_timestamp" in val_names:
        events[str(index)].vmap["start_timestamp"] = pd.to_datetime(
            getattr(row, "event_start_timestamp")
        )
    else:
        events[str(index)].vmap["start_timestamp"] = pd.to_datetime(
            getattr(row, "event_timestamp")
        )


def safe_split(row_obj):
    try:
        if "{" in row_obj:
            return [x.strip() for x in row_obj[1:-1].split(",")]

        else:
            return row_obj.split(",")
    except TypeError:
        return []  # f'NA-{next(counter)}'


def add_obj(
    objects: dict[str, Obj],
    index: int,
    objs: list[tuple[str, str]],
    obj_event_mapping: dict[str, list[str]],
) -> None:
    for obj_id, obj_typ in objs:
        if obj_id not in objects:
            objects[obj_id] = Obj(id=obj_id, type=obj_typ, ovmap={})
        if obj_id in obj_event_mapping:
            obj_event_mapping[obj_id].append(str(index))
        else:
            obj_event_mapping[obj_id] = [str(index)]


def name_type(typ: str) -> str:
    if typ == "object":
        return "string"
    else:
        return typ
