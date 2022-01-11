from typing import Dict, List


<<<<<<< HEAD
class JsonParseParameters(object):
=======
class VmapParameters:
    def __init__(self, vmap_params=None):
        self.vmap_params = vmap_params


class JsonParseParameters(VmapParameters):
>>>>>>> ocpn-functions
    # Mapping from internal event keys to data internal keys
    event_params: Dict[str, str]
    # Mapping from internal object keys to data internal keys
    obj_params: Dict[str, str]
    # Mapping from internal log keys to data internal keys
    log_params: Dict[str, str]

<<<<<<< HEAD
    def __init__(self):
=======
    def __init__(self, vmap_params):
        super().__init__(vmap_params)
>>>>>>> ocpn-functions
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


<<<<<<< HEAD
class CsvParseParameters(object):
=======
class CsvParseParameters(VmapParameters):
>>>>>>> ocpn-functions
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
