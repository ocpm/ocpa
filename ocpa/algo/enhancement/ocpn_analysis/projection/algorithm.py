from ocpa.algo.enhancement.ocpn_analysis.projection.versions import project_on_object_types
from ocpa.algo.enhancement.ocpn_analysis.projection.versions import project_on_subprocess
from ocpa.algo.enhancement.ocpn_analysis.projection.versions import hide

OBJECT_TYPES = "object_types"
SUBPROCESS = "subprocess"
HIDING = "hiding"

VERSIONS = {OBJECT_TYPES: project_on_object_types.apply,
            SUBPROCESS: project_on_subprocess.apply,
            HIDING: hide.apply}


def apply(ocpn, variant=OBJECT_TYPES, parameters=None):
    return VERSIONS[variant](ocpn, parameters=parameters)
