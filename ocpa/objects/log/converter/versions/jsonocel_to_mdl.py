import pandas as pd


def apply(ocel, return_obj_df=True, parameters=None):
    if parameters is None:
        parameters = {}
    if 'return_obj_df' in parameters:
        return_obj_df = parameters['return_obj_df']
    else:
        return_obj_df = True

    prefix = "ocel:"

    objects = ocel.raw.objects
    events = ocel.raw.events

    obj_type = {}
    for obj in objects:
        obj_type[objects[obj].id] = objects[obj].type
    eve_stream = []
    for ev in events:
        # print(events[ev])
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
            if k2.startswith("event_"):
                el[k2] = events[ev].vmap[k2]
            else:
                el["event_" + k2] = events[ev].vmap[k2]
        for k2 in new_omap:
            el[k2] = new_omap[k2]
        eve_stream.append(el)

    obj_stream = []

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
