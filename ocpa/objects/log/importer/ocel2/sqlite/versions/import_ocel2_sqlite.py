from ocpa.objects.log.ocel import OCEL
from typing import Dict, List, Any, Union

def apply(filepath, parameters: Dict) -> OCEL:
    log = None
    obj = None
    graph = None
    table_parameters = None
    ocel = OCEL(log, obj, graph, table_parameters)
    return ocel