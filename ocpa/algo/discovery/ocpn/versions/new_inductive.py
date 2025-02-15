from pm4py.algo.discovery.inductive import algorithm as inductive_miner
from pm4py.objects.petri_net.utils.networkx_graph import create_networkx_directed_graph_ret_dict_both_ways
from pm4py.objects.petri_net.utils.petri_utils import add_arc_from_to
from pm4py.objects.petri_net.utils.petri_utils import remove_place, remove_transition
from pm4py.objects.petri_net.obj import PetriNet
from ocpa.algo.util.util import project_log, project_log_with_object_count
from ocpa.objects.oc_petri_net.obj import ObjectCentricPetriNet
from ocpa.objects.log.importer.csv.util import succint_mdl_to_exploded_mdl, clean_frequency, clean_arc_frequency, \
    clean_normalized_frequency
import pandas as pd
import time
import networkx as nx
import uuid

MAX_FREQUENCY = float("inf")


def reduce_petri_net(net):
    transes = set([x for x in net.transitions if x.label is None])
    places = list(net.places)
    i = 0
    while i < len(places):
        place = places[i]
        source_transes = set([x.source for x in place.in_arcs])
        target_transes = set([x.target for x in place.out_arcs])
        if len(source_transes) == 1 and len(target_transes) == 1:
            if source_transes.issubset(transes) and target_transes.issubset(transes):
                source_trans = list(source_transes)[0]
                target_trans = list(target_transes)[0]
                if len(target_trans.out_arcs) == 1:
                    target_place = list(target_trans.out_arcs)[0].target
                    add_arc_from_to(source_trans, target_place, net)
                    remove_place(net, place)
                    remove_transition(net, target_trans)
                    places = list(net.places)
                    continue
                    # print(source_trans, target_trans, target_place)
        i = i + 1

    return net


def discover_inductive(log):
    return inductive_miner.apply(log)


def discover_nets(df, discovery_algorithm=discover_inductive, parameters=None):
    if parameters is None:
        parameters = {}

    df = succint_mdl_to_exploded_mdl(df, parameters)
    if "event_variant" in df.columns.values:
        df = df.drop('event_variant', axis=1)

    if len(df) == 0:
        df = pd.DataFrame({"event_id": [], "event_activity": []})

    activity_threshold: float = parameters["activity_threshold"] if "activity_threshold" in parameters else 0.0
    min_node_freq = parameters["min_node_freq"] if "min_node_freq" in parameters else 0
    min_edge_freq = parameters["min_edge_freq"] if "min_edge_freq" in parameters else 0

    df = clean_normalized_frequency(df, activity_threshold)
    df = clean_frequency(df, min_node_freq)
    df = clean_arc_frequency(df, min_edge_freq)

    if len(df) == 0:
        df = pd.DataFrame({"event_id": [], "event_activity": []})

    persps = [x for x in df.columns if not x.startswith("event_")]

    ret = {}
    ret["nets"] = {}
    ret["object_count"] = {}

    for persp in persps:
        log = project_log(df, persp, parameters=parameters)
        net, im, fm = discovery_algorithm(log)
        object_count = project_log_with_object_count(df, persp, parameters=parameters)
        ret["nets"][persp] = [net, im, fm]
        ret["object_count"][persp] = object_count

    return ret


def apply(df, discovery_algorithm=discover_inductive, parameters=None):
    ret = discover_nets(df, discovery_algorithm, parameters)
    nets = ret["nets"]
    object_count_persp = ret["object_count"]
    places = []
    transitions = []
    arcs = []
    place_mapping = {}
    transition_mapping = {}
    arc_mapping = {}
    for index, persp in enumerate(nets):
        net, im, fm = nets[persp]
        pl_count = 1
        object_count = object_count_persp[persp]
        for pl in net.places:
            p_name = "%s%d" % (persp, pl_count)
            pl_count += 1
            if pl in im:
                p = ObjectCentricPetriNet.Place(name=p_name,
                                                object_type=persp, initial=True)
            elif pl in fm:
                p = ObjectCentricPetriNet.Place(
                    name=p_name, object_type=persp, final=True)
            else:
                p = ObjectCentricPetriNet.Place(
                    name=p_name, object_type=persp)
            place_mapping[pl] = p
            places.append(p)

        for tr in net.transitions:
            t = None
            for _, new_t in transition_mapping.items():
                if tr.label == new_t.label:
                    t = new_t
            if t is None:
                this_uuid = str(uuid.uuid4())
                if tr.label != "" and tr.label != None:
                    t = ObjectCentricPetriNet.Transition(
                        name=this_uuid, label=tr.label)
                else:
                    t = ObjectCentricPetriNet.Transition(
                        name=this_uuid, label=this_uuid, silent=True)
                transitions.append(t)
            transition_mapping[tr] = t

        for arc in net.arcs:
            if type(arc.source) == PetriNet.Transition:
                t = transition_mapping[arc.source]
                p = place_mapping[arc.target]
                if arc.source.label in object_count and sum(object_count[arc.source.label]) != len(
                        object_count[arc.source.label]):
                    a = ObjectCentricPetriNet.Arc(t, p, variable=True)
                else:
                    a = ObjectCentricPetriNet.Arc(t, p)
                p.in_arcs.add(a)
                t.out_arcs.add(a)
                arcs.append(a)
            else:
                t = transition_mapping[arc.target]
                p = place_mapping[arc.source]
                if arc.target.label in object_count and sum(object_count[arc.target.label]) != len(
                        object_count[arc.target.label]):
                    a = ObjectCentricPetriNet.Arc(p, t, variable=True)
                else:
                    a = ObjectCentricPetriNet.Arc(p, t)

                p.out_arcs.add(a)
                t.in_arcs.add(a)
                arcs.append(a)
            arc_mapping[arc] = a
    ocpn = ObjectCentricPetriNet(
        places=set(places), transitions=set(transitions), arcs=set(arcs), nets=nets, place_mapping=place_mapping,
        transition_mapping=transition_mapping, arc_mapping=arc_mapping)
    return ocpn
