from ocpa.objects.oc_petri_net.obj import ObjectCentricPetriNet


def apply(ocpn: ObjectCentricPetriNet, parameters):

    if 'selected_transition_labels' in parameters:
        selected_transition_labels = parameters['selected_transition_labels']
        selected_transitions = set()
        for l in selected_transition_labels:
            for t in ocpn.transitions:
                if t.name == l:
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

    print(new_places)
    # print(new_transitions)
    # print(new_arcs)

    new_ocpn = ObjectCentricPetriNet(name=ocpn.name + '-projected', places=new_places,
                                     transitions=new_transitions, arcs=new_arcs, properties=ocpn.properties, nets=ocpn.nets)
    return new_ocpn
