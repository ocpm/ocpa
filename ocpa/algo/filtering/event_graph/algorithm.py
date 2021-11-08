from ocpa.algo.filtering.event_graph.versions import filter_object_types
from ocpa.algo.filtering.event_graph.versions import filter_subprocess
from ocpa.algo.filtering.event_graph.versions import filter_complete

OBJECT_TYPES = "object_types"
SUBPROCESS = "subprocess"
COMPLETE = "complete"

VERSIONS = {OBJECT_TYPES: filter_object_types.apply,
            SUBPROCESS: filter_subprocess.apply, COMPLETE: filter_complete.apply}


# def apply(ocpn, cegs, variant=OBJECT_TYPES, parameters=None):
#     return VERSIONS[variant](ocpn, cegs, parameters=parameters)

def apply(subprocess, ceg, variant=SUBPROCESS, parameters=None):
    return VERSIONS[variant](subprocess, ceg, parameters=parameters)
