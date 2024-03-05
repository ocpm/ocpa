import json
from collections import OrderedDict
from datetime import datetime
from typing import Any, Dict, List, Union

import pandas as pd

import ocpa.objects.log.converter.factory as convert_factory
import ocpa.objects.log.variants.util.table as table_utils
from ocpa.objects.log.importer.ocel.parameters import JsonParseParameters
from ocpa.objects.log.ocel import OCEL
from ocpa.objects.log.variants.graph import EventGraph
from ocpa.objects.log.variants.obj import (
    Event,
    MetaObjectCentricData,
    Obj,
    ObjectCentricEventLog,
    RawObjectCentricData,
)
from ocpa.objects.log.variants.table import Table

# import logging
# import pickle


"""
Limitation of the current approach (ocpa v1.2 @25-04-2023):
If an OCEL (JSON/XML) defines an object type as a global parameter,
but this object type is never referenced by an event,
the returned pd.DataFrame(s) will not have the object type as a column.
As other pieces of code depend on this (i.e. the alignment of object types
in the global-log parameters and returned columns here), this will propagate
an error in some other places.
"""


def apply(filepath, parameters: dict, file_path_object_attribute_table=None) -> OCEL:
    if parameters is None:
        parameters = {}
    obj = import_jsonocel(filepath)
    eve_df, obj_df = convert_factory.apply(obj, variant="json_to_csv")
    obj_df = None
    if file_path_object_attribute_table:
        obj_df = pd.read_csv(file_path_object_attribute_table)
    table_parameters = {
        "obj_names": obj.meta.obj_types,  # good
        # TODO check this in a future release
        # "val_names": obj.meta.attr_types,
        "val_names": [
            "event_".join(name) for name in obj.meta.attr_events
        ],  # (table_parameters['val_names'] BAD)
        "act_name": "event_activity",
        "time_name": "event_timestamp",
        "sep": ",",
    }

    table_parameters.update(parameters)  # obj_names good
    # TODO see here (table_parameters['val_names'] is concatenated incorrectly)
    log = Table(log=eve_df, parameters=table_parameters, object_attributes=obj_df)
    graph = EventGraph(table_utils.eog_from_log(log))
    ocel = OCEL(log, obj, graph, parameters=table_parameters)
    return ocel


def import_jsonocel(file_path, parameters=None) -> ObjectCentricEventLog:
    with open(file_path, "rb") as F:
        obj = json.load(F)
    return parse_json(obj)


def parse_json(data: dict[str, Any]) -> ObjectCentricEventLog:
    cfg = JsonParseParameters()
    # parses the given dict
    events, obj_event_mapping = parse_events(data[cfg.log_params["events"]], cfg)
    objects = parse_objects(data[cfg.log_params["objects"]], cfg)
    # Uses the last found value type
    attr_events = {
        v: str(type(events[eid].vmap[v])) for eid in events for v in events[eid].vmap
    }
    attr_objects = {
        v: str(type(objects[oid].ovmap[v]))
        for oid in objects
        for v in objects[oid].ovmap
    }
    attr_types = list(
        {attr_events[v] for v in attr_events}.union(
            {attr_objects[v] for v in attr_objects}
        )
    )
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
    meta = MetaObjectCentricData(
        attr_names=data[cfg.log_params["meta"]][cfg.log_params["attr_names"]],
        obj_types=data[cfg.log_params["meta"]][cfg.log_params["obj_types"]],
        attr_types=attr_types,
        attr_typ=attr_typ,
        act_attr=act_attr,
        attr_events=list(attr_events.keys()),
    )
    return ObjectCentricEventLog(
        meta, RawObjectCentricData(events, objects, obj_event_mapping)
    )


def parse_timestamp(t: str) -> datetime:
    if t.endswith("Z"):
        t = t[:-1]
    return datetime.fromisoformat(t)


def parse_events(
    data: dict[str, Any], cfg: JsonParseParameters
) -> tuple[dict[str, Event], dict]:
    # Transform events dict to list of events
    act_name = cfg.event_params["act"]
    omap_name = cfg.event_params["omap"]
    vmap_name = cfg.event_params["vmap"]
    time_name = cfg.event_params["time"]
    events = {}
    obj_event_mapping = {}
    eid = 0
    for item in data.items():
        events[eid] = Event(
            id=eid,
            act=item[1][act_name],
            omap=item[1][omap_name],
            vmap=item[1][vmap_name],
            time=parse_timestamp(item[1][time_name]),
        )
        if "start_timestamp" not in item[1][vmap_name]:
            events[eid].vmap["start_timestamp"] = parse_timestamp(item[1][time_name])
        else:
            events[eid].vmap["start_timestamp"] = parse_timestamp(
                events[eid].vmap["start_timestamp"]
            )

        for oid in item[1][omap_name]:
            if oid in obj_event_mapping:
                obj_event_mapping[oid].append(eid)
            else:
                obj_event_mapping[oid] = [eid]
        eid += 1

    sorted_events = sorted(events.items(), key=lambda kv: kv[1].time)
    return OrderedDict(sorted_events), obj_event_mapping


def parse_objects(data: dict[str, Any], cfg: JsonParseParameters) -> dict[str, Obj]:
    # Transform objects dict to list of objects
    type_name = cfg.obj_params["type"]
    ovmap_name = cfg.obj_params["ovmap"]
    objects = {
        item[0]: Obj(id=item[0], type=item[1][type_name], ovmap=item[1][ovmap_name])
        for item in data.items()
    }
    return objects
