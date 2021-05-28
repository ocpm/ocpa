import json

import pandas as pd
from dateutil import parser
from lxml import etree, objectify
import dateutil
from jsonschema import validate
import jsonschema
from datetime import datetime


def apply(ocel, return_obj_df=True, parameters=None):
    if parameters is None:
        parameters = {}

    prefix = "ocel:"

    objects = ocel.raw.objects
    events = ocel.raw.events

    obj_type = {}
    for obj in objects:
        obj_type[objects[obj].id] = objects[obj].type

    eve_stream = []
    for ev in events:
        new_omap = {}
        for obj in events[ev].omap:
            typ = obj_type[obj]
            if not typ in new_omap:
                new_omap[typ] = set()
            new_omap[typ].add(obj)
        for typ in new_omap:
            new_omap[typ] = list(new_omap[typ])
        el = {}
        el["event_id"] = events[ev].id
        el["event_activity"] = events[ev].act
        el["event_timestamp"] = events[ev].time
        for k2 in events[ev].vmap:
            el["event_" + k2] = events[ev].vmap[k2]
        for k2 in new_omap:
            el[k2] = new_omap[k2]
        eve_stream.append(el)

    obj_stream = []

    eve_df = pd.DataFrame(eve_stream)
    obj_df = pd.DataFrame(obj_stream)

    eve_df.type = "succint"

    if return_obj_df or (return_obj_df is None and len(obj_df.columns) > 1):
        return eve_df, obj_df
    return eve_df
