from ocpa.algo.util.process_executions.versions import connected_components
from ocpa.algo.util.process_executions.versions import leading_type
<<<<<<< HEAD

CONN_COMP = "connected_components"
LEAD_TYPE = "leading_type"
=======
from ocpa.util.constants import CONN_COMP, LEAD_TYPE
>>>>>>> upstream/main

VERSIONS = {CONN_COMP: connected_components.apply, LEAD_TYPE: leading_type.apply}


def apply(ocel, variant=CONN_COMP, parameters=None):
    return VERSIONS[variant](ocel, parameters=parameters)
