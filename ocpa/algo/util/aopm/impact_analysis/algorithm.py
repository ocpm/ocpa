import datetime
from ocpa.objects.aopm.action_interface_model.obj import Configuration, ActionInstance
from ocpa.algo.util.aopm.impact_analysis.versions import action_interface_model_based
from ocpa.objects.log.ocel import OCEL
from typing import Tuple


AIM_BASED = "action_interface_model_based"
VERSIONS = {
    AIM_BASED: action_interface_model_based.apply
}


def apply(ai: ActionInstance, config: Configuration, ocel: OCEL, tw: Tuple[datetime.datetime, datetime.datetime], variant=AIM_BASED, parameters=None):
    return VERSIONS[variant](ai, config, ocel, tw, parameters=parameters)
