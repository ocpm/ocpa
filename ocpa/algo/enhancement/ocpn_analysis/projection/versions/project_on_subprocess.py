from ocpa.objects.oc_petri_net.obj import ObjectCentricPetriNet
from pm4py.objects.petri_net.utils.networkx_graph import create_networkx_directed_graph_ret_dict_both_ways
import networkx as nx
from pm4py.objects.petri_net.obj import PetriNet


def apply(ocpn: ObjectCentricPetriNet, parameters):
    if 'object_type' in parameters:
        ot = parameters['object_type']
    else:
        raise ValueError('Select object type')

    net, im, fm = ocpn.nets[ot]

    if 'source' in parameters:
        for tr in net.transitions:
            if tr.label == parameters['source']:
                source = tr

    if 'target' in parameters:
        for tr in net.transitions:
            if tr.label == parameters['target']:
                target = tr

    graph, dictionary, inv_dictionary = create_networkx_directed_graph_ret_dict_both_ways(
        net)
    TC = nx.transitive_closure(graph, reflexive=False)
    # paths = nx.all_simple_paths(
    #     graph, source=dictionary[source], target=dictionary[target])
    # nodes = set()
    # for path in paths:
    #     for node in path:
    #         nodes.add(node)

    new_transitions = set()
    new_places = set()
    pn_elements = [inv_dictionary[node] for node in graph.nodes if (
        dictionary[source], node) in TC.edges() and (node, dictionary[target]) in TC.edges()]
    for pn_element in pn_elements:
        if type(pn_element) == PetriNet.Transition:
            new_transitions.add(ocpn.transition_mapping[pn_element])
        else:
            new_places.add(ocpn.place_mapping[pn_element])

    new_arcs = set()
    for arc in net.arcs:
        if arc.source in pn_elements and arc.target in pn_elements:
            new_arcs.add(ocpn.arc_mapping[arc])

    new_ocpn = ObjectCentricPetriNet(name=ocpn.name + '-projected', places=new_places,
                                     transitions=new_transitions, arcs=new_arcs)
    return new_ocpn


def old_apply(ocpn: ObjectCentricPetriNet, parameters):

    if 'selected_transition_labels' in parameters:
        selected_transition_labels = parameters['selected_transition_labels']
        selected_transitions = set()
        for l in selected_transition_labels:
            for t in ocpn.transitions:
                if t.label == l:
                    selected_transitions.add(t)
        # selected_transitions = set(
        #     [t for t in ocpn.transitions for l in selected_transition_labels if t.label == l])
    else:
        selected_transitions = ocpn.transitions

    temp_new_places = list()
    for t in selected_transitions:
        in_out_places = [arc.source for arc in t.in_arcs] + \
            [arc.target for arc in t.out_arcs]
        temp_new_places += in_out_places
    new_places = [p for p in temp_new_places if p in ocpn.places]
    new_places = set(new_places)

    new_transitions = selected_transitions

    new_arcs = set()
    available_nodes = new_places.union(new_transitions)
    for arc in ocpn.arcs:
        if arc.source in available_nodes and arc.target in available_nodes:
            new_arcs.add(arc)
        else:
            continue
    # print(new_transitions)
    # print(new_arcs)

    new_ocpn = ObjectCentricPetriNet(name=ocpn.name + '-projected', places=new_places,
                                     transitions=new_transitions, arcs=new_arcs, properties=ocpn.properties, nets=ocpn.nets)
    return new_ocpn
