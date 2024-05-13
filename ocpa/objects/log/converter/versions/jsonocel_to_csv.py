import pandas as pd

from ocpa.objects.log.variants.obj import ObjectCentricEventLog

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


def apply(
    ocel: ObjectCentricEventLog, return_obj_df=True, parameters=None
) -> tuple[pd.DataFrame, pd.DataFrame]:
    if parameters is None:
        parameters = {}
    if "return_obj_df" in parameters:
        return_obj_df = parameters["return_obj_df"]

    prefix = "ocel:"
    objects = ocel.raw.objects
    events = ocel.raw.events

    obj_type = {}
    for obj in objects:
        obj_type[objects[obj].id] = objects[obj].type
    eve_stream = []
    for ev in events:
        # print(events[ev])
        new_omap = {ot: set() for ot in ocel.meta.obj_types}
        for obj in events[ev].omap:
            new_omap[obj_type[obj]].add(obj)
        for typ in new_omap:
            new_omap[typ] = list(new_omap[typ])
        el = {}
        el["event_id"] = events[ev].id
        el["event_activity"] = events[ev].act
        el["event_timestamp"] = events[ev].time
        for k2 in events[ev].vmap:
            if k2.startswith("event_"):
                el[k2] = events[ev].vmap[k2]
            else:
                el["event_" + k2] = events[ev].vmap[k2]
        for k2 in new_omap:
            el[k2] = new_omap[k2]
        eve_stream.append(el)

    eve_df = pd.DataFrame(eve_stream)
    # if an object is empty for an event, replace them with empty list []
    for col in eve_df.columns:
        if "event" not in col:
            eve_df[col] = eve_df[col].apply(lambda d: d if isinstance(d, list) else [])
    eve_df.type = "succint"

    obj_stream = []
    obj_df = pd.DataFrame(obj_stream)

    if return_obj_df or (return_obj_df is None and len(obj_df.columns) > 1):
        return eve_df, obj_df
    return eve_df, None
