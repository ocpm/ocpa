import logging
import math
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
    if parameters is None:
        parameters = {}

    obj_df = pd.DataFrame()
    if "objects_table" in parameters:
        obj_df = parameters["objects_table"]

    events = {}
    objects = {}
    acts = set()

    df.sort_values(by="event_timestamp", inplace=True)
    obj_names = set([x for x in df.columns if not x.startswith("event_")])
    val_names = set([x for x in df.columns if x.startswith("event_")]) - {"event_activity", "event_timestamp",
                                                                          "event_start_timestamp"}
    obj_event_mapping = {}

    for index, row in enumerate(df.itertuples(), 1):
        add_event(events, index, row, obj_names, val_names)
        objs = [(oid, ot) for ot in obj_names if hasattr(row, ot) for oid in getattr(row, ot)]
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
    objects = add_obj_attributes(
        objects_found_in_event_references=objects, objects_table=obj_df
    )
    logging.debug("*" * 128)
    logging.debug(type(objects))
    logging.debug(_sample_dict(3, objects))
    raw = RawObjectCentricData(
        events=events, objects=objects, obj_event_mapping=obj_event_mapping
    )
    return ObjectCentricEventLog(meta, raw)


def add_obj_attributes(
        objects_found_in_event_references: dict[str, Obj], objects_table: pd.DataFrame
) -> dict[str, Obj]:
    """
    This function adds object attributes to an already existing dict of objects (of type Obj).
    Therefore it might not be optimally efficient, as all Obj in the Obj dict are replaced by
    newly instantiated Obj objects that do have object attributes (Obj.ovmap is filled)
    """
    if objects_table.empty:
        # if objects_table not passed in parameters dict of apply()
        return objects_found_in_event_references

    # select only rows from objects table that occur in the OCEL
    objects_table = objects_table.loc[
        objects_table["object_id"].isin(objects_found_in_event_references.keys())
    ]

    # get a dataframe that retrieves from previously instantiated Obj-list the object type for each object_id
    object_types = pd.DataFrame(
        {oid: [obj.type] for oid, obj in objects_found_in_event_references.items()}
    ).T.rename(columns={"index": "object_id", 0: "object_type"})
    # make join that adds an object type column to the objects (incl. attributes) table/dataframe
    objects_table = (
        objects_table.set_index("object_id")
        .join(object_types, on="object_id")
        .reset_index()
    )
    # object attribute columns/names
    oa_cols = objects_table.columns[1:-1]

    def safe_isnan(x: Any) -> bool:
        if type(x) == float:
            return math.isnan(x)
        return False

    def get_ovmap(object_attribute_values: list[Any]) -> dict[str, Any]:
        """
        Impure utility function (uses oa_cols from outside the function)
        that returns the ovmap given a list of object attribute values.
        It only includes non-nan values (implying that each object type receives its own attributes*)

        * Issue with this method is that if an object has a NULL/None/nan value for an attribute
        that it should have, this attribute will be excluded from its OVMAP
        """

        return {
            k: v
            for (k, v) in zip(oa_cols, object_attribute_values)
            if not safe_isnan(v)
        }

    def create_obj(row: list[Any]) -> Obj:
        ovmap = get_ovmap(object_attribute_values=row[1:-1])
        return Obj(id=row[0], type=row[-1], ovmap=ovmap)

    # create dict with filled with Obj found in objects_table (incl obj attributes),
    # and merge it with the already existing dict of Obj objects (found in the events table)
    objects_found_in_event_references |= {
        row[0]: create_obj(row) for row in objects_table.values.tolist()
    }

    return objects_found_in_event_references


def add_event(
        events: dict[str, Event], index: int, row, obj_names: set[str], val_names: set[str]
) -> None:
    events[str(index)] = Event(
        id=str(index),
        act=getattr(row, "event_activity"),
        time=pd.to_datetime(getattr(row, "event_timestamp")),
        omap=[o for obj in obj_names if hasattr(row, obj) for o in getattr(row, obj)],
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
