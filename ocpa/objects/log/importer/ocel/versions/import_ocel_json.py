import json
from typing import Dict, List, Any

import pandas as pd
from datetime import datetime
from collections import OrderedDict

from ocpa.objects.log.importer.ocel.parameters import JsonParseParameters
from ocpa.objects.log.obj import Event, Obj, ObjectCentricEventLog, MetaObjectCentricData, RawObjectCentricData


def apply(file_path, parameters=None):
    if parameters is None:
        parameters = {}

    if 'return_df' in parameters:
        return_df = parameters['return_df']
    else:
        return_df = False

    if 'return_obj_df' in parameters:
        return_obj_df = parameters['return_obj_df']
    else:
        return_obj_df = None

    if 'start_timestamp' in parameters:
        start_time_col = parameters['start_timestamp']
    else:
        start_time_col = None

    if return_df:
        prefix = "ocel:"
        F = open(file_path, "rb")
        obj = json.load(F)
        F.close()
        eve_stream = obj[prefix + "events"]
        for el in eve_stream:
            eve_stream[el]["event_id"] = el
        obj_stream = obj[prefix + "objects"]
        for el in obj_stream:
            obj_stream[el]["object_id"] = el
        obj_stream = list(obj_stream.values())
        obj_type = {}
        for el in obj_stream:
            obj_type[el["object_id"]] = el[prefix + "type"]
            el["object_type"] = el[prefix + "type"]
            del el[prefix + "type"]
            for k2 in el[prefix + "ovmap"]:
                el["object_" + k2] = el[prefix + "ovmap"][k2]
            del el[prefix + "ovmap"]
        eve_stream = list(eve_stream.values())
        for el in eve_stream:
            new_omap = {}
            for obj in el[prefix + "omap"]:
                typ = obj_type[obj]
                if not typ in new_omap:
                    new_omap[typ] = set()
                new_omap[typ].add(obj)
            for typ in new_omap:
                new_omap[typ] = list(new_omap[typ])
            el[prefix + "omap"] = new_omap
            el["event_activity"] = el[prefix + "activity"]
            el["event_timestamp"] = datetime.fromisoformat(
                el[prefix + "timestamp"])
            del el[prefix + "activity"]
            del el[prefix + "timestamp"]
            for k2 in el[prefix + "vmap"]:
                if k2 == start_time_col:
                    el["event_" + start_time_col] = el[prefix + start_time_col]
                else:
                    el["event_" + k2] = el[prefix + "vmap"][k2]
            # el["event_" + start_time_col] = el[prefix + start_time_col]
            del el[prefix + "vmap"]
            for k2 in el[prefix + "omap"]:
                el[k2] = el[prefix + "omap"][k2]
            del el[prefix + "omap"]

        eve_df = pd.DataFrame(eve_stream)
        # if an object is empty for an event, replace them with empty list []
        for col in eve_df.columns:
            if 'event' not in col:
                eve_df[col] = eve_df[col].apply(
                    lambda d: d if isinstance(d, list) else [])

        obj_df = pd.DataFrame(obj_stream)

        eve_df.type = "succint"

        if return_obj_df or (return_obj_df is None and len(obj_df.columns) > 1):
            return eve_df, obj_df
        return eve_df
    else:
        F = open(file_path, "rb")
        obj = json.load(F)
        F.close()
        return parse_json(obj)


def parse_json(data: Dict[str, Any]) -> ObjectCentricEventLog:
    cfg = JsonParseParameters()
    # parses the given dict
    events = parse_events(data[cfg.log_params['events']], cfg)
    objects = parse_objects(data[cfg.log_params['objects']], cfg)
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
    meta = MetaObjectCentricData(attr_names=data[cfg.log_params['meta']][cfg.log_params['attr_names']],
                                 obj_types=data[cfg.log_params['meta']
                                                ][cfg.log_params['obj_types']],
                                 attr_types=attr_types,
                                 attr_typ=attr_typ,
                                 act_attr=act_attr,
                                 attr_events=list(attr_events.keys()))
    data = ObjectCentricEventLog(
        meta, RawObjectCentricData(events, objects))
    return data


def parse_events(data: Dict[str, Any], cfg: JsonParseParameters) -> Dict[str, Event]:
    # Transform events dict to list of events
    act_name = cfg.event_params['act']
    omap_name = cfg.event_params['omap']
    vmap_name = cfg.event_params['vmap']
    time_name = cfg.event_params['time']
    events = {}
    for item in data.items():
        events[item[0]] = Event(id=item[0],
                                act=item[1][act_name],
                                omap=item[1][omap_name],
                                vmap=item[1][vmap_name],
                                time=datetime.fromisoformat(item[1][time_name]))
        if "start_timestamp" not in item[1][vmap_name]:
            events[item[0]].vmap["start_timestamp"] = None
        else:
            events[item[0]].vmap["start_timestamp"] = datetime.fromisoformat(
                events[item[0]].vmap["start_timestamp"])
    sorted_events = sorted(events.items(), key=lambda kv: kv[1].time)
    return OrderedDict(sorted_events)


def parse_objects(data: Dict[str, Any], cfg: JsonParseParameters) -> Dict[str, Obj]:
    # Transform objects dict to list of objects
    type_name = cfg.obj_params['type']
    ovmap_name = cfg.obj_params['ovmap']
    objects = {item[0]: Obj(id=item[0],
                            type=item[1][type_name],
                            ovmap=item[1][ovmap_name])
               for item in data.items()}
    return objects
