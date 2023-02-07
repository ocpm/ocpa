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

    # def __init__(self, ocpn, integrity_rules=set(), reaction_rules=set(), derivation_rules=set()):
    #     self._ocpn = ocpn
    #     self._integrity_rules = integrity_rules
    #     self._reaction_rules = reaction_rules
    #     self._derivation_rules = derivation_rules

    # @property
    # def ocpn(self) -> ObjectCentricPetriNet:
    #     return self._ocpn

    # @ocpn.setter
    # def ocpn(self, ocpn: ObjectCentricPetriNet) -> None:
    #     self._ocpn = ocpn

    # @property
    # def integrity_rules(self) -> Set[IntegrityRule]:
    #     return self._integrity_rules

    # @integrity_rules.setter
    # def integrity_rules(self, integrity_rules: Set[IntegrityRule]) -> None:
    #     self._integrity_rules = integrity_rules

    # @property
    # def reaction_rules(self) -> Set[ReactionRule]:
    #     return self._reaction_rules

    # @reaction_rules.setter
    # def reaction_rules(self, reaction_rules: Set[ReactionRule]) -> None:
    #     self._reaction_rules = reaction_rules

    # @property
    # def derivation_rules(self) -> Set[DerivationRule]:
    #     return self._derivation_rules

    # @derivation_rules.setter
    # def derivation_rules(self, derivation_rules: Set[DerivationRule]) -> None:
    #     self._derivation_rules = derivation_rules

    # @property
    # def marking(self):
    #     return self._marking

    # @marking.setter
    # def marking(self, marking):
    #     self._marking = marking

    # def set_default_control(self, valves, write_operations):
    #     self._default_control = (valves, write_operations)

    # def get_guard(self, transition: ObjectCentricPetriNet.Transition) -> Guard:
    #     for guard in self._guards:
    #         if guard.transition == transition:
    #             return guard
    #     return None

    # def add_guard(self, tr_name: str, expression: str):
    #     transition = self._ocpn.find_transition(tr_name)
    #     temp_valves = re.findall("\{(.*?)\}", expression)
    #     valves = set([v for v in self._valves if v.name in temp_valves])

    #     guard = Guard(expression, transition, valves)
    #     self._guards.add(guard)

    # def get_tokens_in_place(self, p: ObjectCentricPetriNet.Place):
    #     tokens_in_p = set()
    #     for (pl, oi) in self._marking.tokens:
    #         if pl == p:
    #             tokens_in_p.add((pl, oi))
    #     return tokens_in_p

    # def relate_pre_places(self, t):
    #     results = {}
    #     results["pre_places"] = set()
    #     self._relate_pre_places(t, results)
    #     return results["pre_places"]

    # def _relate_pre_places(self, t: ObjectCentricPetriNet.Transition, results: Dict[str, Set[ObjectCentricPetriNet.Place]]) -> None:
    #     if len(t.preset) == 0:
    #         return
    #     for pl in t.preset:
    #         results["pre_places"].add(pl)
    #         for pre_tr in pl.preset:
    #             tr_preset = pre_tr.preset
    #             results["pre_places"].update(tr_preset)
    #             self._relate_pre_places(pre_tr, results)


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
