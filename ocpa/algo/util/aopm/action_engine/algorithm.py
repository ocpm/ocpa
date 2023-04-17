from typing import List
from ocpa.algo.util.aopm.action_engine.versions import temporal_pattern_based
from ocpa.objects.aopm.action_engine.obj import ConstraintInstance, ConstraintPattern


TEMPORAL_PATTERN_BASED = "temporal_pattern_based"
VERSIONS = {
    TEMPORAL_PATTERN_BASED: temporal_pattern_based.apply
}


def apply(cis:List[ConstraintInstance], cp:ConstraintPattern, variant=TEMPORAL_PATTERN_BASED):
    return VERSIONS[variant](cis, cp)
