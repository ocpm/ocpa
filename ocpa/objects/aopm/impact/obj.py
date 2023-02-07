from dataclasses import dataclass, field
from ocpa.objects.oc_petri_net.obj import ObjectCentricPetriNet
from ocpa.objects.oc_petri_net.obj import Marking
from typing import List, Dict, Any, Optional, Set, Tuple
import datetime
from ocpa.objects.aopm.action_interface_model.obj import ActionInterfaceModel


@dataclass
class ActionChange(object):
    aim: ActionInterfaceModel
    transitions: Set[ObjectCentricPetriNet.Transition]
    tw: Tuple[datetime.datetime, datetime.datetime]


@dataclass
class FunctionWiseStructuralImpact(object):
    elements: Set[ObjectCentricPetriNet.Transition]


@dataclass
class ObjectWiseStructuralImpact(object):
    elements: Set[str]


@dataclass
class OperationalImpact(object):
    elements: Set[str]


@dataclass
class FunctionWisePerformanceImpact(object):
    elements: Dict[ObjectCentricPetriNet.Transition, float]


@dataclass
class ObjectWisePerformanceImpact(object):
    elements: Dict[str, float]
