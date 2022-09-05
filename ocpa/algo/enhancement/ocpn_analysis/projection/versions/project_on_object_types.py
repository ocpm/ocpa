from ocpa.objects.oc_petri_net.obj import ObjectCentricPetriNet


def apply(ocpn: ObjectCentricPetriNet, parameters):

    if 'selected_object_types' in parameters:
        selected_object_types = parameters['selected_object_types']
        print("You selected: {}".format(selected_object_types))
    else:
        selected_object_types = ocpn.object_types

    new_places = set([
        p for p in ocpn.places if p.object_type in selected_object_types])
    new_transitions = set()
    for t in ocpn.transitions:
        in_out_places = [arc.source for arc in t.in_arcs] + \
            [arc.target for arc in t.out_arcs]
        for p in new_places:
            if p in in_out_places:
                new_transitions.add(t)

    new_arcs = set()
    available_nodes = new_places.union(new_transitions)
    for arc in ocpn.arcs:
        if arc.source in available_nodes and arc.target in available_nodes:
            new_arcs.add(arc)
        else:
            continue

    # print(new_places)
    # print(new_transitions)
    # print(new_arcs)

    # update in/out arcs of a transition
    for new_t in new_transitions:
        old_t_in_arcs = set(
            [arc for arc in new_t.in_arcs if arc not in new_arcs])
        for old_in_arc in old_t_in_arcs:
            new_t.in_arcs.remove(old_in_arc)
        old_t_out_arcs = set(
            [arc for arc in new_t.out_arcs if arc not in new_arcs])
        for old_out_arc in old_t_out_arcs:
            new_t.out_arcs.remove(old_out_arc)

    # update in/out arcs of a place
    for new_p in new_places:
        old_t_in_arcs = set(
            [arc for arc in new_p.in_arcs if arc not in new_arcs])
        for old_in_arc in old_t_in_arcs:
            new_p.in_arcs.remove(old_in_arc)
        old_t_out_arcs = set(
            [arc for arc in new_p.out_arcs if arc not in new_arcs])
        for old_out_arc in old_t_out_arcs:
            new_p.out_arcs.remove(old_out_arc)

    new_ocpn = ObjectCentricPetriNet(name=ocpn.name + '-projected', places=new_places,
                                     transitions=new_transitions, arcs=new_arcs, properties=ocpn.properties, nets=ocpn.nets)

    return new_ocpn
