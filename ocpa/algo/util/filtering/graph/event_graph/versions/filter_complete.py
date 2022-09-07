from ocpa.objects.oc_petri_net.obj import ObjectCentricPetriNet


def apply(ocpn: ObjectCentricPetriNet, cegs, parameters):

    if 'selected_object_types' in parameters:
        selected_object_types = parameters['selected_object_types']
    else:
        selected_object_types = ocpn.object_types

    selected_object_types = ocpn.object_types
    print(selected_object_types)
