from pm4py.algo.discovery.alpha import algorithm as alpha_miner
from pm4py.algo.discovery.inductive import algorithm as inductive_miner
from pm4py.algo.discovery.dfg import algorithm as dfg_discovery
from pm4py.statistics.start_activities.log import get as sa_get
from pm4py.statistics.end_activities.log import get as ea_get
from pm4py.objects.conversion.dfg import converter as dfg_converter
# from pm4py.algo.filtering.log.attributes import attributes_filter
from pm4py.objects.petri.utils import add_arc_from_to
from pm4py.objects.petri.utils import remove_place, remove_transition
from ocpa.algo.util.util import project_log, project_log_with_object_count
from ocpa.objects.oc_petri_net.obj import ObjectCentricPetriNet
from ocpa.objects.log.importer.csv.util import succint_mdl_to_exploded_mdl, clean_frequency, clean_arc_frequency
import pandas as pd
import time

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


def discover_alpha(log):
    return alpha_miner.apply(log)


def discover_inductive(log):
    return inductive_miner.apply(log)


def discover_dfg_miner(log):
    dfg = dfg_discovery.apply(log)
    sa = sa_get.get_start_activities(log)
    ea = ea_get.get_end_activities(log)
    net, im, fm = dfg_converter.apply(
        dfg, parameters={"start_activities": sa, "end_activities": ea})
    return net, im, fm


def discover_nets(df, discovery_algorithm=discover_inductive, parameters=None):
    if parameters is None:
        parameters = {}

    allowed_activities = parameters["allowed_activities"] if "allowed_activities" in parameters else None
    debug = parameters["debug"] if "debug" in parameters else True

    df = succint_mdl_to_exploded_mdl(df)
    if "event_variant" in df.columns.values:
        df = df.drop('event_variant', axis=1)

    if len(df) == 0:
        df = pd.DataFrame({"event_id": [], "event_activity": []})

    min_node_freq = parameters["min_node_freq"] if "min_node_freq" in parameters else 0
    min_edge_freq = parameters["min_edge_freq"] if "min_edge_freq" in parameters else 0

    df = clean_frequency(df, min_node_freq)
    df = clean_arc_frequency(df, min_edge_freq)

    if len(df) == 0:
        df = pd.DataFrame({"event_id": [], "event_activity": []})

    persps = [x for x in df.columns if not x.startswith("event_")]

    ret = {}
    ret["nets"] = {}
    ret["object_count"] = {}

    diff_log = 0

    for persp in persps:
        aa = time.time()
        if debug:
            print(persp, "getting log")
        log = project_log(df, persp, parameters=parameters)
        # print(log)
        if debug:
            print(log)
            print(len(log))

        # if allowed_activities is not None:
        #     if persp not in allowed_activities:
        #         continue
        #     filtered_log = attributes_filter.apply_events(
        #         log, allowed_activities[persp])
        # else:
        #     filtered_log = log
        bb = time.time()

        diff_log += (bb - aa)

        if debug:
            print(len(log))
            print(persp, "got log")

        cc = time.time()
        net, im, fm = discovery_algorithm(log)
        dd = time.time()
        diff_log += (dd - cc)

        if debug:
            print(len(log))
            print(persp, "discovered net")

        object_count = project_log_with_object_count(
            df, persp, parameters=parameters)

        ret["nets"][persp] = [net, im, fm]
        ret["object_count"][persp] = object_count

    return ret


def apply(df, discovery_algorithm=discover_inductive, parameters=None):
    ret = discover_nets(df, discovery_algorithm, parameters)
    nets = ret["nets"]
    object_count_persp = ret["object_count"]
    transitions = {}
    transition_list = []
    places = []
    arcs = []
    for index, persp in enumerate(nets):
        net, im, fm = nets[persp]
        for tr in net.transitions:
            if not (tr.label != "" and tr.label != None):
                tr.name = persp + tr.name
        pl_count = 1
        object_count = object_count_persp[persp]
        for pl in net.places:
            p = None
            p_name = "%s%d" % (persp, pl_count)
            # also change the name of the net to synchronize with the resulting ocpn
            pl.name = p_name
            pl_count += 1
            # check if initial
            if pl in im:
                p = ObjectCentricPetriNet.Place(name=pl.name,
                                                object_type=persp, initial=True)
            elif pl in fm:
                p = ObjectCentricPetriNet.Place(
                    name=pl.name, object_type=persp, final=True)
            else:
                p = ObjectCentricPetriNet.Place(
                    name=pl.name, object_type=persp)
            places.append(p)

            for arc in pl.in_arcs:
                t = None
                if arc.source.label != "" and arc.source.label != None:
                    if arc.source.label not in transitions.keys():
                        t = ObjectCentricPetriNet.Transition(
                            name=arc.source.label)
                        transitions[arc.source.label] = t
                        transition_list.append(t)
                    else:
                        t = transitions[arc.source.label]
                else:
                    if arc.source.name not in transitions.keys():
                        t = ObjectCentricPetriNet.Transition(
                            name=arc.source.name, silent=True)
                        transitions[arc.source.name] = t
                        transition_list.append(t)
                    else:
                        t = transitions[arc.source.name]

                # add arc
                if arc.source.label in object_count and sum(object_count[arc.source.label]) != len(
                        object_count[arc.source.label]):
                    a = ObjectCentricPetriNet.Arc(t, p, variable=True)
                else:
                    a = ObjectCentricPetriNet.Arc(t, p)
                p.in_arcs.add(a)
                t.out_arcs.add(a)
                arcs.append(a)
            for arc in pl.out_arcs:
                t = None
                if arc.target.label != "" and arc.target.label != None:
                    if arc.target.label not in transitions.keys():
                        t = ObjectCentricPetriNet.Transition(
                            name=arc.target.label)
                        transitions[arc.target.label] = t
                        transition_list.append(t)
                    else:
                        t = transitions[arc.target.label]
                else:
                    if arc.target.name not in transitions.keys():
                        t = ObjectCentricPetriNet.Transition(
                            name=arc.target.name, silent=True)
                        transitions[arc.target.name] = t
                        transition_list.append(t)
                    else:
                        t = transitions[arc.target.name]

                # add arc
                if arc.target.label in object_count and sum(object_count[arc.target.label]) != len(object_count[arc.target.label]):
                    a = ObjectCentricPetriNet.Arc(p, t, variable=True)
                else:
                    a = ObjectCentricPetriNet.Arc(p, t)

                p.out_arcs.add(a)
                t.in_arcs.add(a)
                arcs.append(a)
    ocpn = ObjectCentricPetriNet(
        places=set(places), transitions=set(transition_list), arcs=set(arcs), nets=nets)
    return ocpn
