from ocpa.algo.util.filtering.graph.event_graph.versions import filter_subprocess

# OBJECT_TYPES = "object_types"
SUBPROCESS = "subprocess"
# COMPLETE = "complete"

VERSIONS = {
    # OBJECT_TYPES: filter_object_types.apply,
    SUBPROCESS: filter_subprocess.apply,
    # COMPLETE: filter_complete.apply
}


# def apply(ocpn, cegs, variant=OBJECT_TYPES, parameters=None):
#     return VERSIONS[variant](ocpn, cegs, parameters=parameters)

def apply(subprocess, ceg, variant=SUBPROCESS, parameters=None):
    filtered_ceg = VERSIONS[variant](subprocess, ceg, parameters=parameters)
    if filtered_ceg != None:
        return filtered_ceg
    else:
        return None
