from ocpa.objects.oc_petri_net.obj import ObjectCentricPetriNet
from ocpa.algo.reduction import algorithm as ocpn_reduction_factory


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
    elif 'selected_transitions' in parameters:
        selected_transitions = set(parameters['selected_transitions'])
    else:
        selected_transitions = ocpn.transitions
    print("You selected: {}".format(selected_transitions))

    for t in ocpn.transitions:
        if t in selected_transitions:
            continue
        else:
            t.silent = True

    reduced_ocpn, log = ocpn_reduction_factory.apply(ocpn)

    return reduced_ocpn
