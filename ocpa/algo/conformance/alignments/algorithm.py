import ocpa
#from ocpa.algo.conformance.alignments import helperfunctions
from ocpa.algo.conformance.alignments.helperfunctions import remove_transition_and_connected_arcs
from ocpa.algo.conformance.alignments.helperfunctions import FrozenMarking

# import logging
from typing import List, Set, Dict, Tuple, Optional
import timeit

import networkx as nx
import matplotlib.pyplot as plt
from datetime import datetime
import copy

from ocpa.objects.log.importer.ocel import factory as ocel_import_factory
from ocpa.algo.discovery.ocpn import algorithm as ocpn_discovery_factory
from ocpa.visualization.oc_petri_net import factory as ocpn_vis_factory

from ocpa.objects.oc_petri_net.obj import ObjectCentricPetriNet, Marking
from ocpa.objects.log.ocel import OCEL

from ocpa.objects.graph.process_execution_graph.processexecutiongraph import OCEvent, ProcessExecutionGraph
from ocpa.algo.conformance.alignments.alignment import Alignment, Move, UndefinedModelMove, DefinedModelMove, LogMove, SynchronousMove, \
    UndefinedSynchronousMove, TransitionSignature, DijkstraInfo, Binding



# logging.basicConfig(level=logging.DEBUG, format=' %(asctime)s - %(levelname)s- %(message)s')


transition_to_move_map = dict()


global_trans_properties_key = []
global_trans_properties_value = []
# store original type of places (not the new one that is based on object instances)
# used for original type of px-net places
global_place_properties_key = []
global_place_properties_value = []


def get_all_event_objects(ocel, event_id):
    obj_ids = []
    for obj_type in ocel.object_types:
        obj_ids += ocel.get_value(event_id, obj_type)
    return obj_ids


def get_in_cardinality_of_transition(transition: ObjectCentricPetriNet.Transition) -> Dict[str, int]:
    in_card = dict()
    place: ObjectCentricPetriNet.Place
    for place in transition.preset:
        obj_type = place.object_type
        in_card.setdefault(obj_type, 0)
        in_card[obj_type] += 1
    return in_card


def get_out_cardinality_of_transition(transition: ObjectCentricPetriNet.Transition) -> Dict[str, int]:
    out_card = dict()
    place: ObjectCentricPetriNet.Place
    for place in transition.postset:
        obj_type = place.object_type
        out_card.setdefault(obj_type, 0)
        out_card[obj_type] += 1
    return out_card


def get_in_cardinality_of_transition_px(transition: ObjectCentricPetriNet.Transition) -> Dict[str, int]:
    in_card = dict()
    place: ObjectCentricPetriNet.Place
    for place in transition.preset:
        # property of the place holds original type
        obj_type = get_properties_of_place(place)
        in_card.setdefault(obj_type, 0)
        in_card[obj_type] += 1
    return in_card


def get_out_cardinality_of_transition_px(transition: ObjectCentricPetriNet.Transition) -> Dict[str, int]:
    out_card = dict()
    place: ObjectCentricPetriNet.Place
    for place in transition.postset:
        obj_type = get_properties_of_place(place)
        out_card.setdefault(obj_type, 0)
        out_card[obj_type] += 1
    return out_card


def get_properties_of_transition(transition: ObjectCentricPetriNet.Transition) -> Optional[TransitionSignature]:
    return transition.properties
    # if transition in global_trans_properties_key:
    #     return global_trans_properties_value[global_trans_properties_key.index(transition)]
    # else:
    #     raise Exception()


def set_properties_of_transition(transition: ObjectCentricPetriNet.Transition, properties: TransitionSignature) -> None:
    transition.properties = properties
    # if transition in global_trans_properties_key:
    #     global_trans_properties_value[global_trans_properties_key.index(transition)] = properties
    # else:
    #     global_trans_properties_key.append(transition)
    #     global_trans_properties_value.append(properties)


def get_properties_of_place(place: ObjectCentricPetriNet.Place):
    return place.properties
    # if place in global_place_properties_key:
    #     return global_place_properties_value[global_place_properties_key.index(place)]
    # else:
    #     raise Exception()


def set_properties_of_place(place: ObjectCentricPetriNet.Place, properties) -> None:
    place.properties = properties
    # if place in global_place_properties_key:
    #     global_place_properties_value[global_place_properties_key.index(place)] = properties
    # else:
    #     global_place_properties_key.append(place)
    #     global_place_properties_value.append(properties)


def process_execution_net_from_process_execution(ocel, indirect_id, px, date_format) -> Tuple[ObjectCentricPetriNet,
                                                                                 List[Tuple[ObjectCentricPetriNet.Place,
                                                                                            str]]]:
    initial_marking_list = []
    final_marking_list = []
    # Create process execution Graph (px-graph) from process execution
    px_graph = ProcessExecutionGraph()
    # Get events with related objects
    for event_id in px:
        event = OCEvent()
        event.event_id = event_id
        event.event_name = ocel.get_value(event_id, 'event_activity')
        event.objects = get_all_event_objects(ocel, event_id)
        event.datetime = ocel.get_value(event_id, 'event_timestamp')
        px_graph.add_event(event)

    px_graph.update_dependencies()
    # px_graph.show()

    # Start with empty petri net for the px-net
    px_net = ObjectCentricPetriNet()
    # Add all start places
    current_front_place = dict()
    number_of_places = dict()
    list_of_obj_instances_in_px = ocel.process_execution_objects[indirect_id]
    list_of_obj_instances_in_px = [(obj_type, obj_instance) for obj_type, obj_instance in list_of_obj_instances_in_px]
    #print(f"Object Instances: {list_of_obj_instances_in_px}")
    for obj_type, obj_instance in list_of_obj_instances_in_px:
        #print(f"Obj instance: {obj_instance}")
        number_of_places[obj_instance] = 1
        # Note how the type is the object instance! This creates a different type for each instance:
        place = ObjectCentricPetriNet.Place(name=f"({obj_instance} - s1)", object_type=obj_instance, initial=True)
        # store original type of place
        set_properties_of_place(place, obj_type)
        current_front_place[obj_instance] = place
        px_net.places.add(place)
        initial_marking_list.append((place, obj_instance))

    # Add leaf nodes from the process execution graph until empty
    num_of_transition = 0
    while not px_graph.is_empty():
        num_of_transition += 1
        next_event = px_graph.drop_next_event_leaf_to_head()
        #print('')
        #print(next_event)
        #print('')
        # px_graph.show()

        # add transition to px-net
        # create move
        log_move = LogMove(next_event.event_name, next_event.objects)
        # XXX Here is the Move assigned to the transition in the properties property
        transition = ObjectCentricPetriNet.Transition(name=f"px-{next_event.event_name}-{num_of_transition}",
                                                      label=f"px-{next_event.event_name}-{num_of_transition}")
        px_net.transitions.add(transition)
        # add arcs for transition
        for obj_instance in next_event.objects:
            # to transition
            arc = ObjectCentricPetriNet.Arc(current_front_place[obj_instance], transition)
            px_net.add_arc(arc)
            # from transition
            number_of_places[obj_instance] += 1
            place = ObjectCentricPetriNet.Place(name=f"({obj_instance} - {number_of_places[obj_instance]})",
                                                object_type=obj_instance)
            px_net.places.add(place)
            # set properties (original_type) of place
            original_type = \
                [obj_type for obj_type, obj_inst in list_of_obj_instances_in_px if obj_inst == obj_instance][0]
            set_properties_of_place(place, original_type)

            arc = ObjectCentricPetriNet.Arc(transition, place)
            px_net.add_arc(arc)
            current_front_place[obj_instance] = place

        # create signature of transition
        in_card = get_in_cardinality_of_transition_px(transition)
        out_card = get_out_cardinality_of_transition_px(transition)
        # change the already assigned properties attribute of transition
        transition_signature_for_created_transition = TransitionSignature(name=next_event.event_name,
                                                                          in_cardinality=in_card,
                                                                          out_cardinality=out_card,
                                                                          move=log_move)
        set_properties_of_transition(transition, transition_signature_for_created_transition)
        # trans_prop = get_properties_of_transition(transition)
        # #print(f"Transitions property: {get_properties_of_transition(transition)}")

    # make current front places to final places
    for obj_instance, final_place in current_front_place.items():
        #print(final_place)
        final_place.final = True
        # final_place = helperfunctions.set_place_to_final(final_place, px_net)
        final_marking_list.append((final_place, obj_instance))

    # visualize px_net
    ##ocpn_vis_factory.save(ocpn_vis_factory.apply(px_net), "px_net.png")

    return (px_net, initial_marking_list, final_marking_list)


def create_all_transitions(ocpn: ObjectCentricPetriNet,
                           transition: ObjectCentricPetriNet.Transition,
                           in_variable_arcs_by_type: Dict[str, ObjectCentricPetriNet.Arc],
                           out_variable_arcs_by_type: Dict[str, ObjectCentricPetriNet.Arc],
                           undefined_cardinality: List[Tuple[str, int]],
                           defined_cardinality: List[Tuple[str, int]]):
    # recursion stopping criteria
    if not undefined_cardinality:
        cardinality_string = ""
        for cardinality_tuple in defined_cardinality:
            cardinality_string += f" {cardinality_tuple[1]}"

        #print(f"Create new Transition {transition.name} with defeined: {defined_cardinality} undefined: {undefined_cardinality}")

        # create in and out cardinatlity for signature
        # can be different from parameter one in case of multiple variable arcs with same type
        card_signature_in = dict()
        card_signature_out = dict()

        # add transition with defined cardinality for each type
        # XXX Silent transition when previous one was silent
        # XXX ToDo
        new_transition = ObjectCentricPetriNet.Transition(f"{transition.name} {cardinality_string}",
                                                          f"{transition.label} {cardinality_string}")
        ocpn.transitions.add(new_transition)
        number_of_arcs_created: int = 0
        # add ingoing arcs
        arc: ObjectCentricPetriNet.Arc
        for arc in transition.in_arcs:
            if not arc.variable:
                # copy arc (with new target)
                new_arc = ObjectCentricPetriNet.Arc(arc.source, new_transition)
                ocpn.add_arc(new_arc)
                # update signature
                # card_signature_in.setdefault(arc.source.object_type, 0)
                # card_signature_in[arc.source.object_type] += 1 XXX Danger: we assume arcs of same type come from
                # different places
                card_signature_in.setdefault(arc.source.object_type, 1)
                number_of_arcs_created += 1
            else:
                # check type and add as many arcs as defined by type
                source: ObjectCentricPetriNet.Place = arc.source
                type = source.object_type
                # XXX maybe unsafe because we get index 0 without checking if empty (but it should not be empty if
                # correct net)
                cardinality_for_given_type: int = [card for def_type, card in defined_cardinality if def_type == type][
                    0]
                for i in range(cardinality_for_given_type):
                    new_arc = ObjectCentricPetriNet.Arc(source, new_transition)
                    ocpn.add_arc(new_arc)
                # update signature
                if cardinality_for_given_type > 0:
                    # card_signature_in.setdefault(type, 0)
                    # card_signature_in[type] += cardinality_for_given_type
                    card_signature_in.setdefault(type, cardinality_for_given_type)
                    number_of_arcs_created += cardinality_for_given_type
        # add outgoing arcs
        arc: ObjectCentricPetriNet.Arc
        for arc in transition.out_arcs:
            if not arc.variable:
                # copy arc (with new source)
                new_arc = ObjectCentricPetriNet.Arc(new_transition, arc.target)
                ocpn.add_arc(new_arc)
                # card_signature_out.setdefault(arc.target.object_type, 0)
                # card_signature_out[arc.target.object_type] += 1
                card_signature_out.setdefault(arc.target.object_type, 1)  # XXX Danger look ar in arcs for explanation
            else:
                # check type and add as many arcs as defined by type
                target: ObjectCentricPetriNet.Place = arc.target
                type = target.object_type
                # XXX may be unsafe because we get index 0 without checking if empty (but it should not be empty if
                # correct net)
                list_card = [card for def_type, card in defined_cardinality if def_type == type]
                cardinality_for_given_type: int = list_card[0]
                for i in range(cardinality_for_given_type):
                    new_arc = ObjectCentricPetriNet.Arc(new_transition, target)
                    ocpn.add_arc(new_arc)
                if cardinality_for_given_type > 0:
                    # card_signature_out.setdefault(type, 0)
                    # card_signature_out[type] += cardinality_for_given_type
                    card_signature_out.setdefault(type, cardinality_for_given_type)
                number_of_arcs_created += cardinality_for_given_type

        # LUKASLISS
        # get the signature
        signature_in = dict()
        help_place = dict()  # used to only use first place of each type to get cardinality
        for in_arc in new_transition.in_arcs:
            help_place.setdefault(in_arc.source.object_type, in_arc.source)
            if help_place[in_arc.source.object_type] == in_arc.source:
                signature_in.setdefault(in_arc.source.object_type, 0)
                signature_in[in_arc.source.object_type] += 1

        # add signature to transition
        model_move = UndefinedModelMove(model_move=transition.name, objects=None, silent=transition.silent)
        set_properties_of_transition(new_transition, TransitionSignature(transition.name, signature_in,
                                                                         signature_in, model_move))
        # trans_prop = get_properties_of_transition(new_transition)
        # #print(f"Transitions property: {get_properties_of_transition(new_transition)}")

        # XXX Optimization: calculate the in and out cardinalities for signature already in recursion steps
        if number_of_arcs_created <= 0:
            # delete unconnected transitions
            ocpn.remove_transition(new_transition)
    else:
        # define one type and go in recursion
        type_yet_undefined, max_instances = undefined_cardinality[0]
        for defined_value in range(max_instances + 1):
            new_undefined_list = undefined_cardinality[1:]  # because first is now defined
            new_defined_list = defined_cardinality[:]
            new_defined_list.append((type_yet_undefined, defined_value))
            create_all_transitions(ocpn, transition, in_variable_arcs_by_type, out_variable_arcs_by_type,
                                   new_undefined_list, new_defined_list)


def preprocessing_dejure_net(ocel: OCEL, indirect_id, ocpn):
    # find number of instances per object type
    px_objects = ocel.process_execution_objects[indirect_id]
    type_to_number_of_instance_map = dict()
    for type, instance in px_objects:
        if type not in type_to_number_of_instance_map.keys():
            type_to_number_of_instance_map[type] = 0
        type_to_number_of_instance_map[type] += 1
    #print(type_to_number_of_instance_map)

    # go through all the transitions to check whether they have variable arcs
    transition: ObjectCentricPetriNet.Transition
    original_transitions = list(ocpn.transitions)
    for transition in original_transitions:
        transition_has_variable = False
        in_variable_arcs_by_type = dict()
        out_variable_arcs_by_type = dict()
        # ingoing arcs
        arc: ObjectCentricPetriNet.Arc
        for arc in transition.in_arcs:
            if arc.variable:
                transition_has_variable = True
                # the type of the arc can be received by getting the type of the place that is the source
                if arc.source.object_type not in in_variable_arcs_by_type.keys():
                    in_variable_arcs_by_type[arc.source.object_type] = []
                in_variable_arcs_by_type[arc.source.object_type].append(arc)
        # outgoing arcs
        arc: ObjectCentricPetriNet.Arc
        for arc in transition.out_arcs:
            if arc.variable:
                transition_has_variable = True
                if arc.target.object_type not in out_variable_arcs_by_type.keys():
                    out_variable_arcs_by_type[arc.target.object_type] = []
                out_variable_arcs_by_type[arc.target.object_type].append(arc)

        if not transition_has_variable:
            # set signature and then continue
            card_signature_in = dict()  # only in cardinality is needed because in and out have to be the same

            help_place = dict()  # helps to only use the first place per object type for cardinality analysis
            for in_arc in transition.in_arcs:
                help_place.setdefault(in_arc.source.object_type, in_arc.source)
                if help_place[in_arc.source.object_type] == in_arc.source:
                    card_signature_in.setdefault(in_arc.source.object_type, 0)
                    card_signature_in[in_arc.source.object_type] += 1

            model_move = UndefinedModelMove(model_move=transition.name, objects=None, silent=transition.silent)
            set_properties_of_transition(transition, TransitionSignature(transition.name, card_signature_in,
                                                                             card_signature_in, model_move))
            continue

        # transition has variable arcs connected and need preprocessing:
        #print(f"Var. Trans: {transition.name}")
        # create initial list of all variable types together with their max number of instances
        undefined_cardinality = []
        defined_cardinality = []
        for key, value in type_to_number_of_instance_map.items():
            if ((key in in_variable_arcs_by_type.keys()) or (key in out_variable_arcs_by_type.keys())):
                undefined_cardinality.append((key, value))
        create_all_transitions(ocpn, transition, in_variable_arcs_by_type, out_variable_arcs_by_type,
                               undefined_cardinality,
                               defined_cardinality)
        # break  # just testing
        # remove transition with variable arc
        remove_transition_and_connected_arcs(transition, ocpn)
    # XXX Optimization dissolve list that stores all the deleted transitions with variable arcs (they are not needed)

    # Create initial and final marking list
    initial_marking_list = []
    final_marking_list = []
    list_of_obj_instances_in_px = ocel.process_execution_objects[indirect_id]
    list_of_obj_instances_in_px = [(obj_type, obj_instance) for obj_type, obj_instance in list_of_obj_instances_in_px]
    place: ObjectCentricPetriNet.Place
    for place in ocpn.places:
        if place.initial:
            for obj_type, obj_instance in list_of_obj_instances_in_px:
                if obj_type == place.object_type:
                    initial_marking_list.append((place, obj_instance))
        if place.final:
            for obj_type, obj_instance in list_of_obj_instances_in_px:
                if obj_type == place.object_type:
                    final_marking_list.append((place, obj_instance))

    # visualize the preprocessed pn
    #ocpn_vis_factory.save(ocpn_vis_factory.apply(ocpn), "pre_processed_dejure_net.png")

    return initial_marking_list, final_marking_list


def create_synchronous_product_net(px_net: ObjectCentricPetriNet,
                                   px_ini_mark_list: List[Tuple[ObjectCentricPetriNet.Place, str]],
                                   px_fin_mark_list: List[Tuple[ObjectCentricPetriNet.Place, str]],
                                   dejure_net: ObjectCentricPetriNet,
                                   dejure_ini_mark_list: List[Tuple[ObjectCentricPetriNet.Place, str]],
                                   dejure_fin_mark_list: List[Tuple[ObjectCentricPetriNet.Place, str]], ) \
        -> Tuple[ObjectCentricPetriNet, FrozenMarking,
                 FrozenMarking]:
    sync_net = ObjectCentricPetriNet(name="Synchronous Product Net")
    # add both given nets to sync net
    petrinet: ObjectCentricPetriNet
    for petrinet in [px_net, dejure_net]:
        for transition in petrinet.transitions:
            sync_net.transitions.add(transition)
        for place in petrinet.places:
            sync_net.places.add(place)
        for arc in petrinet.arcs:
            sync_net.add_arc(arc)
    # add synchronous moves
    number_of_sync = 0
    px_transition: ObjectCentricPetriNet.Transition
    for px_transition in px_net.transitions:
        px_signature = get_properties_of_transition(px_transition)
        for dejure_transition in dejure_net.transitions:
            dejure_signature = get_properties_of_transition(dejure_transition)
            if px_signature == dejure_signature:
                number_of_sync += 1
                # create the synchronous transition
                #print(f"Sync found: {px_transition.name} and {dejure_transition.name}")
                sync_transition = ObjectCentricPetriNet.Transition(name=f"sync - {px_signature.name}-{number_of_sync}",
                                                                   label=f"sync - {px_signature.name}-{number_of_sync}")
                undefined_syn_move = UndefinedSynchronousMove(px_signature.name)
                # XXX Optimization: The signature is not needed for the synchronous moves
                # it is just added to make it the same as all other transitions
                signature = TransitionSignature(name=px_signature.name,
                                                in_cardinality=px_signature.in_cardinality,
                                                out_cardinality=px_signature.out_cardinality,
                                                move=undefined_syn_move)
                set_properties_of_transition(sync_transition, signature)

                # add transition and all arcs to the synchronous product net
                sync_net.transitions.add(sync_transition)
                related_px_in_arcs: ObjectCentricPetriNet.Arc
                # ingoing from px net
                for related_px_in_arcs in px_transition.in_arcs:
                    new_arc = ObjectCentricPetriNet.Arc(related_px_in_arcs.source, sync_transition)
                    sync_net.add_arc(new_arc)
                    undefined_syn_move.px_preset.add(related_px_in_arcs.source)
                related_dejure_in_arcs: ObjectCentricPetriNet.Arc
                # ingoing from dejure net
                for related_dejure_in_arcs in dejure_transition.in_arcs:
                    new_arc = ObjectCentricPetriNet.Arc(related_dejure_in_arcs.source, sync_transition)
                    sync_net.add_arc(new_arc)
                    undefined_syn_move.dejure_preset.add(related_dejure_in_arcs.source)
                # postset can be handled all at once
                for any_outgoing_arc in px_transition.out_arcs | dejure_transition.out_arcs:
                    new_arc = ObjectCentricPetriNet.Arc(sync_transition, any_outgoing_arc.target)
                    sync_net.add_arc(new_arc)

    # merge initial and final markings
    initial_marking_list = px_ini_mark_list + dejure_ini_mark_list
    final_marking_list = px_fin_mark_list + dejure_fin_mark_list
    initial_marking_sync = FrozenMarking(frozenset(initial_marking_list))
    final_marking_list_sync = FrozenMarking(frozenset(final_marking_list))
    return sync_net, initial_marking_sync, final_marking_list_sync


def alignment_from_dijkstra(visited: Dict[FrozenMarking, DijkstraInfo], end_marking):
    move_stack = []

    current_marking = end_marking
    dij_info = visited[current_marking]
    while dij_info.previous_marking is not None:
        move_stack.insert(0, dij_info.move_to_this)
        dij_info = visited[dij_info.previous_marking]
    return Alignment(move_stack)


def create_all_bindings(pn: ObjectCentricPetriNet, transition: ObjectCentricPetriNet.Transition,
                        current_marking: FrozenMarking,
                        num_by_type_in: Dict[str, int], availabel_by_type_in: Dict[str, Set[str]],
                        chosen_by_type_in: Dict[str, Set[str]]) -> List[
    Tuple[ObjectCentricPetriNet.Transition, Binding, Move, FrozenMarking]]:
    # Copy recursion relevant lists to prevent side effects
    num_by_type = copy.deepcopy(num_by_type_in)
    available_by_type = copy.deepcopy(availabel_by_type_in)
    chosen_by_type = copy.deepcopy(chosen_by_type_in)

    if not num_by_type.keys():
        # the binding is done
        move = get_properties_of_transition(transition).move

        # XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
        # XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
        # Check whether the binding complies with nue-net requirement
        # XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
        # XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
        if isinstance(move, UndefinedSynchronousMove):
            # get instances of all the chosen types
            instances_from_px = set()
            instances_from_dejure = set()

            for place, obj_id in current_marking.tokens:
                if place in move.px_preset:
                    if obj_id in chosen_by_type[place.object_type]:
                        instances_from_px.add(obj_id)
                if place in move.dejure_preset:
                    if obj_id in chosen_by_type[place.object_type]:
                        instances_from_dejure.add(obj_id)

            # Binding not valid if nue-net requirement not fulfilled
            if not instances_from_dejure == instances_from_px:
                return []

        binding = Binding(chosen_by_type)

        # calculate Move

        if isinstance(move, UndefinedSynchronousMove):
            object_set = set()
            for obj_id_set in chosen_by_type.values():
                object_set = object_set.union(obj_id_set)
            move = move.get_defined_sync_move(list(object_set))
        if isinstance(move, UndefinedModelMove):
            object_set = set()
            for obj_id_set in chosen_by_type.values():
                object_set = object_set.union(obj_id_set)
            move = move.define(list(object_set))

        # calculate resulting marking
        marking_list = list(current_marking.tokens)
        # wrong consume token
        # for place, obj_id in marking_list:
        #     if place in transition.preset and obj_id in chosen_by_type[place.object_type]:
        #         marking_list.remove((place, obj_id))
        # consume token
        for source in transition.preset:
            for obj_id in chosen_by_type[source.object_type]:
                marking_list.remove((source, obj_id))
        # produce token
        for target in transition.postset:
            for obj_id in chosen_by_type[target.object_type]:
                marking_list.append((target, obj_id))
        resulting_marking = FrozenMarking(frozenset(marking_list))

        return [(transition, binding, move, resulting_marking)]

    # Still types that one needs to choose combinations from
    # chose type
    type_to_define = next(iter(num_by_type.keys()))
    number_to_select = num_by_type[type_to_define]

    if number_to_select <= 0:
        #print("num to select <= 0 in create all")
        pass

    if number_to_select == len(available_by_type[type_to_define]):
        # directly choose all of them (speedup)
        chosen_by_type.setdefault(type_to_define, set())
        for obj_id in available_by_type[type_to_define]:
            chosen_by_type[type_to_define].add(obj_id)
        del available_by_type[type_to_define]

        # remove from num_by_type
        del num_by_type[type_to_define]

        return create_all_bindings(pn, transition, current_marking, num_by_type, available_by_type, chosen_by_type)

    if number_to_select < len(available_by_type[type_to_define]):
        potential_obj_id = next(iter(available_by_type[type_to_define]))

        # use potential one
        use_num_by_type = copy.deepcopy(num_by_type)
        use_available_by_type = copy.deepcopy(available_by_type)
        use_chosen_by_type = copy.deepcopy(chosen_by_type)

        use_chosen_by_type.setdefault(type_to_define, set())
        use_chosen_by_type[type_to_define].add(potential_obj_id)
        use_num_by_type[type_to_define] -= 1
        use_available_by_type[type_to_define].remove(potential_obj_id)
        if use_num_by_type[type_to_define] == 0:
            # no more recursion for this type because all chosen
            del use_num_by_type[type_to_define]
        use_binding_list = create_all_bindings(pn, transition, current_marking, use_num_by_type, use_available_by_type,
                                               use_chosen_by_type)

        # not use potential one
        not_use_num_by_type = copy.deepcopy(num_by_type)  # XXX Optimization not copy but use normal ones
        not_use_available_by_type = copy.deepcopy(available_by_type)
        not_use_chosen_by_type = copy.deepcopy(chosen_by_type)

        not_use_available_by_type[type_to_define].remove(potential_obj_id)
        not_use_binding_list = create_all_bindings(pn, transition, current_marking, not_use_num_by_type,
                                                   not_use_available_by_type, not_use_chosen_by_type)

        return use_binding_list + not_use_binding_list

    if number_to_select > len(available_by_type[type_to_define]):
        raise Exception("Algorithmic Error in Binding Calculation. Number to select is lower than number of objects.")

    raise Exception("Algorithmic Error in Binding Calculation. Unwanted Code Path reached.")


def all_valid_bindings(pn: ObjectCentricPetriNet, current_marking: FrozenMarking) -> List[
    Tuple[ObjectCentricPetriNet.Transition, Binding, Move, FrozenMarking]]:
    if not isinstance(pn, ObjectCentricPetriNet):
        raise Exception("Parameter pn ist not of type ObjectCentricPetriNet")
    if not isinstance(current_marking, FrozenMarking):
        raise Exception("Parameter current_marking ist not of type FrozenMarking")

    all_val_bindings = []
    # for all transitions create all valid bindings
    transition: ObjectCentricPetriNet.Transition
    for transition in pn.transitions:
        # determine how often each type is required by transition as defined by number of ingoing arcs from a place with that type
        number_of_required_objects_by_type = dict()
        help_places = dict()  # dictonary with a place for each type. That place is used to count ingoing arcs
        # determine all the object_instances that are in the intersection of the sets of object_instances in the places from the preset
        # Here the intersection is used because a binding requires the places of the same type to all have the specified objects
        available_obj_instances_by_type: Dict[str, Set[str]] = dict()

        in_arc: ObjectCentricPetriNet.Arc
        for in_arc in transition.in_arcs:
            source_place: ObjectCentricPetriNet.Place = in_arc.source

            # just use one place per object type to determin the number of object ids needed
            help_places.setdefault(source_place.object_type, source_place)
            if help_places[source_place.object_type] == source_place:
                number_of_required_objects_by_type.setdefault(source_place.object_type,
                                                              0)  # XXX Danger if misconstructed PN
                number_of_required_objects_by_type[source_place.object_type] += 1

            obj_ids_in_place = set()
            for place, obj_id in current_marking.tokens:
                if place == source_place:
                    obj_ids_in_place.add(obj_id)
            available_obj_instances_by_type.setdefault(source_place.object_type, obj_ids_in_place)
            available_obj_instances_by_type[source_place.object_type] \
                = available_obj_instances_by_type[source_place.object_type].intersection(obj_ids_in_place)

        # set the chosen objects to an empty set for each type to initalize the recursion
        valid = True
        chosen_obj_ids_by_type = dict()
        for obj_type in number_of_required_objects_by_type.keys():
            if number_of_required_objects_by_type[obj_type] > len(available_obj_instances_by_type[obj_type]):
                valid = False  # the transition can not fire because to less obj_instances for ingoing arcs
                # #print(f"NO: {transition.name} - Transition has no binding")
                break
            chosen_obj_ids_by_type[obj_type] = set()

        # go into the recursion to create all
        if valid:
            all_val_bindings_of_this_transition = create_all_bindings(pn, transition, current_marking,
                                                                      number_of_required_objects_by_type,
                                                                      available_obj_instances_by_type,
                                                                      chosen_obj_ids_by_type)
            # #print(f"YES: {transition.name} - has {len(all_val_bindings_of_this_transition)}")
            all_val_bindings = all_val_bindings + all_val_bindings_of_this_transition

    return all_val_bindings


def dijkstra(sync_net: ObjectCentricPetriNet, ini_marking: FrozenMarking, fin_marking: FrozenMarking) -> Alignment:
    if not isinstance(ini_marking, FrozenMarking):
        Exception("ini_marking is not of type FrozenMarking")
    if not isinstance(fin_marking, FrozenMarking):
        Exception("fin_marking is not of type FrozenMarking")
    if not isinstance(ini_marking, ObjectCentricPetriNet):
        Exception("sync_net is not of type ObjectCentricPetriNet")

    #print("Entering Dijkstra")
    # no state(marking) was visited yet and no marking is reachable yet
    visited = dict()
    reachable = dict()

    # add the start marking with distance 0
    reachable[ini_marking] = DijkstraInfo(previous_marking=None, move_to_this=None, cost=0)

    # while final marking not yet visited:
    while fin_marking not in visited.keys():
        if not reachable.keys():
            raise Exception("Dijkstra did not find a shortest path. Algorithmic error.")
        # select the reachable unvisited marking with the lowest cost
        selected_marking = None
        selected_dij_info: Optional[DijkstraInfo] = None
        for marking, dij_inf in reachable.items():
            if selected_marking is None or dij_inf.cost < selected_dij_info.cost:
                selected_marking = marking
                selected_dij_info = dij_inf

        if(dij_inf.move_to_this == None and dij_inf.previous_marking == None):
            #print("Start was selected")
            pass
        else:
            #print("")
            #print(f"Selected with pre done transition: {selected_dij_info.cost} - {selected_dij_info.move_to_this.model_move} and {selected_dij_info.move_to_this.log_move}")
            pass

        # update the previous marking and the move as well in table
        visited[selected_marking] = reachable[selected_marking]
        del reachable[selected_marking]
        alignment_so_far = alignment_from_dijkstra(visited, selected_marking)
        #print(f"Selected had {len(alignment_so_far.moves)}")
        #print(f"Log  : {[move.log_move for move in alignment_so_far.moves]}")
        #print(f"Model: {[move.model_move for move in alignment_so_far.moves]}")

        # [dij_inf.cost for dij_inf in reachable.values() if dij_inf.cost == 0]
        # if len([(place, obid) for place, obid in selected_marking if (place.name == "MATERIAL6" or place.name == "MATERIAL7")]) > 0:
        #     #print()

        # calculate all the bindings that could fire from the selected marking
        valid_bindings = all_valid_bindings(sync_net, selected_marking)
        #print("", end="")

        # if len([p for p, obid in selected_marking.tokens if (p.name == m1 or p.name == m2)]) > 0:
        #     #print("Possible End")
        #     pass
        # [ transition, binding, move, resulting_marking for transition, binding, move, resulting_marking in valid_bindings if move.model_move == "Goods Issue"]
        # for each binding calculate the resulting marking and cost of firing
        # if cost to selected marking + cost for firing binding is lower than previous distance, update cost
        for transition, binding, move, resulting_marking in valid_bindings:
            sync_found = False
            if move == None:
                #print("move None")
                pass
            if selected_marking == None:
                #print("sel mark None")
                pass
            if isinstance(move, SynchronousMove):
                sync_found = True
                #print(f"Sync move added: {move.model_move} - {move.log_move}")

            if resulting_marking not in reachable.keys() and resulting_marking not in visited.keys():
                # add directly because its first encounter of this marking
                reachable[resulting_marking] = DijkstraInfo(selected_marking, move, selected_dij_info.cost + move.cost)
                if sync_found:
                    #print(f"Sync Cost was: {selected_dij_info.cost + move.cost} - not in ")
                    pass
            if resulting_marking in reachable.keys():
                # add only if shorter way found
                if selected_dij_info.cost + move.cost < reachable[resulting_marking].cost:
                    reachable[resulting_marking] = DijkstraInfo(selected_marking, move, selected_dij_info.cost + move.cost)
                    if sync_found:
                        #print(f"Sync Cost was: {selected_dij_info.cost + move.cost} - was in so update")
                        pass

    alignment = alignment_from_dijkstra(visited, fin_marking)
    #print(f"Final State found with cost: {alignment.get_cost()}")
    #print(f"Log  : {[move.log_move for move in alignment_so_far.moves]}")
    #print(f"Model: {[move.model_move for move in alignment_so_far.moves]}")
    return alignment


def calculate_oc_alignments(ocel: OCEL, extern_ocpn: ObjectCentricPetriNet, date_format='%Y-%m-%d %H:%M:%S%z') -> Dict[str, Alignment]:
    # XXX ToDo Remove once the helper functions are gone
    transition_to_move_map = dict()
    global_trans_properties_key = []
    global_trans_properties_value = []
    # store original type of places (not the new one that is based on object instances)
    # used for original type of px-net places
    global_place_properties_key = []
    global_place_properties_value = []

    # Start: without helper functions
    # if not isinstance(ocel, OCEL):
    #     #print("ocel has to be an instance of OCEL")
    #     raise Exception("Given argument ocel was not an instace of OCEL")
    # if not isinstance(extern_ocpn, ObjectCentricPetriNet):
    #     #print("ocpn has to be an instance of ObjectCentricPetriNet type.")
    #     raise Exception("ocpn has to be an instance of ObjectCentricPetriNet type.")

    #input check
    if not isinstance(ocel, OCEL):
        raise Exception("Parameter ocel is not of type OCEL.")
    if not isinstance(extern_ocpn, ObjectCentricPetriNet):
        raise Exception("Parameter extern_ocpn is not of type ObjectCentricPetriNet.")

    # For each variant use a process execution in the log to calculate an individual alignment
    alignment_dict = dict()
    # laufvariable = 0
    for variant_id in ocel.variants:
        ocpn = copy.deepcopy(extern_ocpn)
        #ocpn_vis_factory.save(ocpn_vis_factory.apply(ocpn), "post_deepcopy_net.png")

        indirect_id = ocel.variants_dict[variant_id][0]  # XXX Check before that it is not empty
        process_execution = ocel.process_executions[indirect_id]

        # Each process execution is a list of event ids
        # Create Event Net
        px_net, px_initial_marking_list, px_final_marking_list = process_execution_net_from_process_execution(ocel,
                                                                                                              indirect_id,
                                                                                                              process_execution, date_format)
        #ocpn_vis_factory.save(ocpn_vis_factory.apply(px_net), "px_net.png")
        # Preprocessing of ocpn to remove variable arcs
        dejure_initial_marking_list, dejure_final_marking_list = preprocessing_dejure_net(ocel, indirect_id, ocpn)
        # Create Synchronous Product Net
        sync_pn, sync_initial_marking, sync_final_marking = create_synchronous_product_net(px_net,
                                                                                           px_initial_marking_list,
                                                                                           px_final_marking_list, ocpn,
                                                                                           dejure_initial_marking_list,
                                                                                           dejure_final_marking_list)
        #ocpn_vis_factory.save(ocpn_vis_factory.apply(sync_pn), "synchronous_product_net.png")
        #print(sync_initial_marking)
        #print(sync_final_marking)
        # Search for shortest path in Synchronous Product Net
        alignment_for_variant = dijkstra(sync_pn, sync_initial_marking, sync_final_marking)
        alignment_for_variant.add_object_types(ocel.process_execution_objects[indirect_id])
        alignment_dict[variant_id] = alignment_for_variant
        #print("Process execution aligned!")
    return alignment_dict

def calculate_oc_alignment_given_variant_id(ocel: OCEL, extern_ocpn: ObjectCentricPetriNet, variant_id, date_format='%Y-%m-%d %H:%M:%S%z') -> Dict[str, Alignment]:
    # For each variant use a process execution in the log to calculate an individual alignment
    alignment_dict = dict()
    # laufvariable = 0

    ocpn = copy.deepcopy(extern_ocpn)
    #ocpn_vis_factory.save(ocpn_vis_factory.apply(ocpn), "post_deepcopy_net.png")

    indirect_id = ocel.variants_dict[variant_id][0]  # XXX Check before that it is not empty
    process_execution = ocel.process_executions[indirect_id]

    # Each process execution is a list of event ids
    # Create Event Net
    px_net, px_initial_marking_list, px_final_marking_list = process_execution_net_from_process_execution(ocel,
                                                                                                          indirect_id,
                                                                                                          process_execution,
                                                                                                          date_format)
    #ocpn_vis_factory.save(ocpn_vis_factory.apply(px_net), "px_net.png")
    # Preprocessing of ocpn to remove variable arcs
    dejure_initial_marking_list, dejure_final_marking_list = preprocessing_dejure_net(ocel, indirect_id, ocpn)
    # Create Synchronous Product Net
    sync_pn, sync_initial_marking, sync_final_marking = create_synchronous_product_net(px_net,
                                                                                       px_initial_marking_list,
                                                                                       px_final_marking_list, ocpn,
                                                                                       dejure_initial_marking_list,
                                                                                       dejure_final_marking_list)
    #ocpn_vis_factory.save(ocpn_vis_factory.apply(sync_pn), "synchronous_product_net.png")
    #print(sync_initial_marking)
    #print(sync_final_marking)
    # Search for shortest path in Synchronous Product Net
    alignment_for_variant = dijkstra(sync_pn, sync_initial_marking, sync_final_marking)
    alignment_for_variant.add_object_types(ocel.process_execution_objects[indirect_id])
    #print("Process execution aligned!")
    return alignment_for_variant
