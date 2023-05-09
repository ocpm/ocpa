from dataclasses import dataclass, field
from ocpa.objects.oc_petri_net.obj import ObjectCentricPetriNet
from ocpa.objects.oc_petri_net.obj import Marking
from typing import List, Dict, Any, Optional, Set, Tuple, Union
import copy


@dataclass
class IntegrityRule(object):
    object_type: str
    expression: str


@dataclass
class ReactionRule(object):
    object_type: str
    expression: str


@dataclass
class DerivationRule(object):
    object_type: str
    expression: str


@dataclass
class ActionInterfaceModel(object):
    ocpn: ObjectCentricPetriNet
    integrity_rules: Set[IntegrityRule]
    reaction_rules: Set[ReactionRule]
    derivation_rules: Set[DerivationRule]

    def to_dict(self):
        return {
            "ocpn": self.ocpn.to_dict()
        }


@dataclass
class Configuration(object):
    aim: ActionInterfaceModel
    integrity_rule_assignment: Dict[ObjectCentricPetriNet.Transition,
                                    Set[IntegrityRule]]
    reaction_rule_assignment: Dict[ObjectCentricPetriNet.Transition,
                                   Set[ReactionRule]]
    derivation_rule_assignment: Dict[ObjectCentricPetriNet.Transition,
                                     Set[DerivationRule]]


@dataclass
class OperationalState(object):
    aim: ActionInterfaceModel
    marking: Marking
    ovmap: Dict[str, Dict[str, any]] = field(default_factory=None)


@dataclass
class IntegrityRuleBasedAction(object):
    aim: ActionInterfaceModel
    update: Dict[ObjectCentricPetriNet.Transition,
                 Set[IntegrityRule]]

    def apply(self, config: Configuration):
        new_integrity_rule_assignment = {
            **config.integrity_rule_assignment, **self.update}
        return Configuration(self.aim, new_integrity_rule_assignment, config.reaction_rule_assignment, config.derivation_rule_assignment)


@dataclass
class ReactionRuleBasedAction(object):
    aim: ActionInterfaceModel
    update: Dict[ObjectCentricPetriNet.Transition, Set[ReactionRule]]


@dataclass
class DerivationRuleBasedAction(object):
    aim: ActionInterfaceModel
    update: Dict[ObjectCentricPetriNet.Transition, Set[DerivationRule]]


@dataclass
class ActionInstance(object):
    aim: ActionInterfaceModel
    action: Union[IntegrityRuleBasedAction,
                  ReactionRuleBasedAction, DerivationRuleBasedAction]
    time_window: Tuple[any, any]
