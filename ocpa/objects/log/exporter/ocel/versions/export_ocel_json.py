from json import dumps, loads, JSONEncoder, JSONDecoder
import pickle
from ocpa.objects.log.variants.obj import Event, Obj, ObjectCentricEventLog
from ocpa.objects.log.util.param import JsonParseParameters
import json
from ocpa.objects.log.ocel import OCEL


def apply(ocel: OCEL, file_path: str, parameters=None):
    cfg = JsonParseParameters(None)
    meta = ocel.obj.meta
    raw = ocel.obj.raw
    export = dict()
    export[cfg.log_params["meta"]] = dict()
    export[cfg.log_params["meta"]][cfg.log_params["attr_names"]] = meta.attr_names
    export[cfg.log_params["meta"]][cfg.log_params["obj_types"]] = meta.obj_types
    export[cfg.log_params["meta"]][cfg.log_params["version"]] = "1.0"
    export[cfg.log_params["meta"]][cfg.log_params["ordering"]] = "timestamp"
    events = {}
    for event in raw.events.values():
        events[event.id] = {}
        events[event.id][cfg.event_params["act"]] = event.act
        events[event.id][cfg.event_params["time"]] = event.time.isoformat()
        events[event.id][cfg.event_params["omap"]] = event.omap
        events[event.id][cfg.event_params["vmap"]] = event.vmap

    objects = {}
    for obj in raw.objects.values():
        objects[obj.id] = {}
        objects[obj.id][cfg.obj_params["type"]] = obj.type
        objects[obj.id][cfg.obj_params["ovmap"]] = obj.ovmap

    export[cfg.log_params["events"]] = events
    export[cfg.log_params["objects"]] = objects
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(export, f, ensure_ascii=False,
                  indent=4, default=str)
    return export


class PythonObjectEncoder(JSONEncoder):
    def default(self, obj):
        try:
            return {'_python_object': pickle.dumps(obj).decode('latin-1')}
        except pickle.PickleError:
            return super().default(obj)


def as_python_object(dct):
    if '_python_object' in dct:
        return pickle.loads(dct['_python_object'].encode('latin-1'))
    return dct
