from typing import Dict, List


class VmapParameters:
    def __init__(self, vmap_params, vmap_availables=None):
        self.vmap_params = vmap_params


class JsonParseParameters(VmapParameters):
    # Mapping from internal event keys to data internal keys
    event_params: Dict[str, str]
    # Mapping from internal object keys to data internal keys
    obj_params: Dict[str, str]
    # Mapping from internal log keys to data internal keys
    log_params: Dict[str, str]

    def __init__(self, vmap_params, vmap_availables):
        super().__init__(vmap_params, vmap_availables)
        self.event_params = {'act': 'ocel:activity',
                             'time': 'ocel:timestamp',
                             'omap': 'ocel:omap',
                             'vmap': 'ocel:vmap'}
        self.obj_params = {'type': 'ocel:type',
                           'ovmap': 'ocel:ovmap'}
        self.log_params = {'attr_names': 'ocel:attribute-names',
                           'obj_types': 'ocel:object-types',
                           'ordering': 'ocel:ordering',
                           'events': 'ocel:events',
                           'objects': 'ocel:objects',
                           'meta': 'ocel:global-log'}


class CsvParseParameters(VmapParameters):
    obj_names: List[str]
    val_names: List[str]
    time_name: str
    act_name: str

    def __init__(self, obj_names, val_names, time_name, act_name, vmap_params, vmap_availables):
        super().__init__(vmap_params, vmap_availables)
        self.obj_names = obj_names
        self.val_names = val_names
        self.time_name = time_name
        self.act_name = act_name
