from os import remove
from ocpa.objects.oc_petri_net.obj import ObjectCentricPetriNet


def FST(ocpn, sacred_nodes):
    for p in ocpn.places:
        #  Check whether the place is sacred. Should not be.
        if p in sacred_nodes:
            continue

        # Check the input arc. There should be only one and it should be
        preset = p.in_arcs
        if len(preset) != 1:
            continue

        in_arc = list(preset)[0]

        # Get the input transition. No additional requirements.
        in_t = in_arc.source

        # Check the output arc. There should be only one, it should be regular, and its weight should be identical.
        postset = p.out_arcs
        if len(postset) != 1:
            continue
        out_arc = list(postset)[0]

        # Get the output transition. Should have only the place as input.
        out_t = out_arc.target
        if len(out_t.in_arcs) != 1:
            continue

        if in_t == out_t:
            continue

        # Found a series transition. Remove if not sacred.
        if out_t not in sacred_nodes:
            log = """<fst place="{}" outputTransition="{}" """.format(
                p.name, out_t.name)

            # (Skip) Transfer tokens from place to postset of output transition.
            # Also, transfer outgoing edges from output transition to input transition.
            postset = out_t.out_arcs
            arcs = ocpn.arcs
            arcs_to_add = set()
            for post_p in postset:
                # Variable arc taken from (input transition -> place)
                arc = ocpn.find_arc(in_t, p)
                new_arc = ObjectCentricPetriNet.Arc(
                    in_t, post_p.target, arc.variable, arc.weight)
                arcs_to_add.add(new_arc)

            ocpn.add_arcs(arcs_to_add)
            ocpn.remove_place(p)
            ocpn.remove_transition(out_t)
            # ocpn = clear_arcs(ocpn)
            return ocpn, log
        elif in_t not in sacred_nodes and (out_t.silent == True or len(in_t.out_arcs) == 1):
            log = """<fst inputTransition="{}" place="{}" """.format(
                in_t.name, p.name)
            # /*
            # * Input transition is not sacred and either the output
            # * transition is invisible or the input transition has only the
            # * place as output. Perhaps some explanation of this last
            # * requirement is in place. Assume that the output transition is
            # * visible, that is, it has a label, and that the input
            # * transition has additional outputs. Then the paths starting at
            # * these additional outputs do not include the output
            # * transition, whereas after reduction they would. Therefore, if
            # * the input transition has additional outputs, then the output
            # * transition must be invisible.
            # *
            # * Remove the input transition. First, update the maps.
            # */

            # (Skip) Transfer tokens from place to preset of input transition.

            # Transfer incoming edges from the input transition to the output transition.
            preset = in_t.in_arcs
            arcs = ocpn.arcs
            arcs_to_add = set()
            for pre_p in preset:
                # Variable arc taken from (place -> output transition)
                arc = ocpn.find_arc(p, out_t)
                new_arc = ObjectCentricPetriNet.Arc(
                    pre_p.source, out_t, arc.variable, arc.weight)
                arcs_to_add.add(new_arc)

            # Transfer outgoing edges from the input transition to the output transition.
            postset = in_t.out_arcs
            for post_p in postset:
                # Variable arc taken from (input transition -> postset)
                arc = ocpn.find_arc(in_t, post_p.target)
                new_arc = ObjectCentricPetriNet.Arc(
                    out_t, post_p, arc.variable, arc.weight)
                arcs_to_add.add(new_arc)

            ocpn.add_arcs(arcs_to_add)
            ocpn.remove_place(p)
            ocpn.remove_transition(in_t)
            return ocpn, log
        # /*
        # * Either both are sacred, or the output transition is sacred and
        # * visible and the input transition has additional outgoing edges.
        # * Any way, the reduction rule does not apply.
        # */
    return ocpn, None


def FSP(ocpn, sacred_nodes):
    for t in ocpn.transitions:
        #  Check whether the place is sacred. Should not be.
        if t in sacred_nodes:
            continue

        # Check the input arc. There should be only one, it should be regular, and it weight should be one.
        preset = t.in_arcs
        if len(preset) != 1:
            continue

        in_arc = list(preset)[0]

        # Get the input place. Should have only the place as output.
        in_p = in_arc.source
        postset = in_p.out_arcs
        if len(postset) != 1:
            continue

        # Check the output arc. There should be only one, it should be regular, and its weight should be one.
        postset = t.out_arcs
        if len(postset) != 1:
            continue
        out_arc = list(postset)[0]
        if in_arc.weight != out_arc.weight:
            continue

        # Get the output place. No additional requirements.
        out_p = out_arc.target
        if len(out_p.in_arcs) != 1:
            continue

        if in_p == out_p:
            continue

        # Found a series place. Remove a place (input or output) that is not sacred.
        if in_p not in sacred_nodes:
            log = """<fsp inputPlace="{}" transition="{}" """.format(
                in_p.name, t.name)

            # (Skip) Move tokens from input place to output place.

            # Also, transfer any input edge from the input place to the output place.

            preset = in_p.in_arcs
            arcs = ocpn.arcs
            arcs_to_add = set()
            for pre_p in preset:
                # Variable arc taken from (preset -> input place)
                arc = ocpn.find_arc(pre_p.source, in_p)
                new_arc = ObjectCentricPetriNet.Arc(
                    pre_p.source, out_p, arc.variable, arc.weight)
                arcs_to_add.add(new_arc)

            ocpn.add_arcs(arcs_to_add)
            ocpn.remove_transition(t)
            ocpn.remove_place(in_p)
            # ocpn = clear_arcs(ocpn)
            return ocpn, log
        elif out_p not in sacred_nodes:
            log = """<fsp transition="{}" outputPlace="{}" """.format(
                in_p.name, t.name)

            # (Skip) Move tokens form output place to input place.

            # * Also, transfer any input edge from the output place to the input place, and any output edge from the output place to the input place.
            preset = out_p.in_arcs
            arcs = ocpn.arcs
            arcs_to_add = set()
            for pre_p in preset:
                # Variable arc taken from (preset -> output place)
                arc = ocpn.find_arc(pre_p.source, out_p)
                new_arc = ObjectCentricPetriNet.Arc(
                    pre_p.source, in_p, arc.variable, arc.weight)
                arcs_to_add.add(new_arc)

            postset = out_p.out_arcs
            arcs = ocpn.arcs
            for post_p in postset:
                # Variable arc taken from (output place -> postset)
                arc = ocpn.find_arc(out_p, post_p.target)
                new_arc = ObjectCentricPetriNet.Arc(
                    in_p, post_p.target, arc.variable, arc.weight)
                arcs_to_add.add(new_arc)

            ocpn.add_arcs(arcs_to_add)
            ocpn.remove_transition(t)
            ocpn.remove_place(out_p)
            return ocpn, log
        # /*
        # * Either both are sacred, or the output transition is sacred and
        # * visible and the input transition has additional outgoing edges.
        # * Any way, the reduction rule does not apply.
        # */
    return ocpn, None


def FPT(ocpn, sacred_nodes):
    # (Skip) Iterate over all transitions. Build inputMap and outputMap if all incident edges regular.

    # Iterate over all transitions with only regular incident edges.
    for t in ocpn.transitions:
        #  Checking for matching transitions.
        for sibling_t in ocpn.transitions:
            if t == sibling_t:
                continue
            if len(t.in_arcs) != len(sibling_t.in_arcs):
                continue

            if len(t.out_arcs) != len(sibling_t.out_arcs):
                continue

            sibling_t_in_arc_sources = [
                in_arc.source for in_arc in sibling_t.in_arcs]
            t_in_arc_sources = [in_arc.source for in_arc in t.in_arcs]

            sibling_t_out_arc_targets = [
                out_arc.target for out_arc in sibling_t.out_arcs]
            t_out_arc_targets = [out_arc.target for out_arc in t.out_arcs]

            if t_in_arc_sources == sibling_t_in_arc_sources and t_out_arc_targets == sibling_t_out_arc_targets:
                equal = True
            else:
                equal = False

            if equal:
                # Found a sibling with identical inputs and outputs. Remove either the sibling or the transition, if allowed.
                # Check whether a sacred nodes is involved.
                if sibling_t in sacred_nodes or t in sacred_nodes:
                    continue

                if sibling_t not in sacred_nodes and t not in sacred_nodes:
                    log = """<fpt siblingTransition="{}" """.format(
                        sibling_t.name)
                    ocpn.remove_transition(sibling_t)
                    return ocpn, log

                elif t not in sacred_nodes:
                    log = """<fpt siblingTransition="{}" """.format(t.name)
                    ocpn.remove_transition(sibling_t)
                    return ocpn, log
    return ocpn, None


def FPP(ocpn, sacred_nodes):
    # (Skip) Iterate over all places. Build inputMap and outputMap if all incident edges regular.

    # Iterate over all places with only regular incident edges.
    for p in ocpn.places:
        #  Checking for matching transitions.
        for sibling_p in ocpn.places:
            if p == sibling_p:
                continue

            # Also check if all in_arcs have the same type
            all_in_acrs = [p_in_arc for p_in_arc in p.in_arcs] + \
                [sibling_p_in_arc for sibling_p_in_arc in sibling_p.in_arcs]
            if ~all(x == all_in_acrs[0] for x in all_in_acrs):
                continue

            if len(p.in_arcs) != len(sibling_p.in_arcs):
                continue

            if len(p.out_arcs) != len(sibling_p.out_arcs):
                continue

            sibling_p_in_arc_sources = [
                in_arc.source for in_arc in sibling_p.in_arcs]
            p_in_arc_sources = [in_arc.source for in_arc in p.in_arcs]

            sibling_p_out_arc_targets = [
                out_arc.target for out_arc in sibling_p.out_arcs]
            p_out_arc_targets = [out_arc.target for out_arc in p.out_arcs]

            if p_in_arc_sources == sibling_p_in_arc_sources and p_out_arc_targets == sibling_p_out_arc_targets:
                equal = True
            else:
                equal = False

            if equal:
                # Found a sibling with identical inputs and outputs. Remove either the sibling or the transition, if allowed.
                # Check whether a sacred nodes is involved.
                if sibling_p in sacred_nodes or p in sacred_nodes:
                    continue

                if sibling_p not in sacred_nodes and p not in sacred_nodes:
                    log = """<fpp siblingPlace="{}" """.format(
                        sibling_p.name)
                    ocpn.remove_place(sibling_p)
                    return ocpn, log

                elif p not in sacred_nodes:
                    log = """<fpp siblingPlace="{}" """.format(p.name)
                    ocpn.remove_place(sibling_p)
                    return ocpn, log
    return ocpn, None


def EST(ocpn, sacred_nodes):
    for t in ocpn.transitions:
        #  Check whether the place is sacred. Should not be.
        if t in sacred_nodes:
            continue

        # Check the input arc. There should be only one, it should be regular, and it weight should be one.
        preset = t.in_arcs
        if len(preset) != 1:
            continue

        in_arc = list(preset)[0]

        # Check the output arc. There should be only one, it should be regular, and its weight should be one.
        postset = t.out_arcs
        if len(postset) != 1:
            continue
        out_arc = list(postset)[0]
        if in_arc.weight != out_arc.weight:
            continue

        # Check wether self loop.
        if in_arc.source != out_arc.target:
            continue

        # Check whether place has other output transitions that needs at least as much tokens as this transition.
        in_p_postset = in_arc.source.out_arcs
        if len(in_p_postset) < 2:
            continue
        ok = False
        for arc in in_p_postset:
            if ok:
                continue
            if arc == in_arc:
                continue
            if arc.weight >= in_arc.weight:
                ok = True

        if ok:
            log = """<elt transition="{}">""".format(t.name)
            # We have a self loop for a transition. Remove the transition.
            ocpn.remove_transition(t)
            return ocpn, log
    return ocpn, None


def ESP(ocpn, sacred_nodes):
    for p in ocpn.places:
        #  Check whether the place is sacred. Should not be.
        if p in sacred_nodes:
            continue

        # Check the input arc. There should be only one and it should be
        preset = p.in_arcs
        if len(preset) != 1:
            continue

        in_arc = list(preset)[0]

        # Check the output arc. There should be only one, it should be regular, and its weight should be identical.
        postset = p.out_arcs
        if len(postset) != 1:
            continue
        out_arc = list(postset)[0]

        if in_arc.weight != out_arc.weight:
            continue

        # Check wether self loop.
        if in_arc.source != out_arc.target:
            continue

        # (Skip) Check whether tokens exceed weight.
        log = """<elp place="{}">""".format(p.name)
        # We have a self loop for a marked place. Remove the place from the copy net. First, update the place map.
        ocpn.remove_place(p)
        return ocpn, log
    return ocpn, None


def apply(ocpn: ObjectCentricPetriNet, parameters):
    visible_transitions = [t for t in ocpn.transitions if t.silent != True]
    initial_final_marking_places = [
        p for p in ocpn.places if p.initial == True or p.final == True]
    sacred_nodes = visible_transitions + initial_final_marking_places

    reduction_rules = [FST, FSP, FPT, FPP, EST, ESP]

    log = ""
    while True:
        log = None
        for rule in reduction_rules:
            if log is None:
                print("Start {}".format(rule))
                ocpn, log = rule(ocpn, sacred_nodes)
                print(log)

        if log is None:
            break
    return ocpn, log
