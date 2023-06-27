from typing import List, Tuple
from ocpa.algo.util.aopm.action_engine.versions import temporal_pattern_based
from ocpa.objects.aopm.action_engine.obj import ConstraintInstance, ActionGraph


TEMPORAL_PATTERN_BASED = "temporal_pattern_based"
VERSIONS = {
    TEMPORAL_PATTERN_BASED: temporal_pattern_based.apply
}


def apply(cis:List[ConstraintInstance], action_graph:List[ActionGraph], action_conflicts:List[Tuple[str,str]], variant=TEMPORAL_PATTERN_BASED):
    return VERSIONS[variant](cis, action_graph, action_conflicts)
