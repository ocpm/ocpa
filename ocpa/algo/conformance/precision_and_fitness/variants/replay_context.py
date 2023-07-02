from itertools import combinations
from collections import Counter
import time
import itertools
from itertools import product
import numpy
from multiprocessing.dummy import Pool as ThreadPool


def context_to_string_verbose(context):
    cstr = ""
    for key in context.keys():
        cstr += key
        for c in context[key].most_common():
            cstr += ",".join(c[0])
            cstr += str(c[1])
    return cstr


def context_to_string(context):
    return hash(tuple([hash(tuple(sorted(context[cc].items()))) for cc in context.keys()]))
    cstr = ""
    for key in context.keys():
        cstr += key
        for c in context[key].most_common():
            cstr += ",".join(c[0])
            cstr += str(c[1])
    return cstr


def model_enabled(model, state, transition):
    enabled = True
    for a in transition.in_arcs:
        if a.source not in state.keys():
            enabled = False
        elif len(state[a.source]) < 1:
            enabled = False
    return enabled


def state_to_place_counter(state):
    result = Counter()
    for p in state.keys():
        result += Counter({p.name: len(state[p])})
    return hash(tuple(sorted(result.items())))


def binding_possible(ocpn, state, binding, object_types):
    if len(binding) == 0:
        return False
    tokens = [o for ot in object_types for o in binding[0][1][ot]]
    input_places_tokens = []
    t = None
    for t_ in ocpn.transitions:
        if t_.label == binding[0][0]:
            t = t_
    if t == None:
        return False
    for a in t.in_arcs:
        input_places_tokens += state[a.source] if a.source in state.keys() else [
        ]
    if set(tokens).issubset(set(input_places_tokens)) or set(tokens) == set(input_places_tokens):
        if model_enabled(ocpn, state, t):
            return True
    return False


def calculate_next_states_on_bindings(ocpn, state, binding, object_types):
    state_update_pairs = []
    possible = True
    if binding_possible(ocpn, state, binding, object_types):
        t = None
        for t_ in ocpn.transitions:
            if t_.label == binding[0][0]:
                t = t_
        in_places = {}
        out_places = {}
        for ot in object_types:
            in_places[ot] = [(x, y) for (x, y) in [(a.source, a.variable)
                                                   for a in t.in_arcs] if x.object_type == ot]
            out_places[ot] = [x for x in [
                a.target for a in t.out_arcs] if x.object_type == ot]
        new_state = {k: state[k].copy() for k in state.keys()}
        update = not t.silent
        for ot in object_types:
            if ot not in binding[0][1].keys():
                continue
            for out_pl in out_places[ot]:
                if out_pl not in new_state.keys():
                    new_state[out_pl] = []
                new_state[out_pl] += list(binding[0][1][ot])

            for (in_pl, is_v) in in_places[ot]:
                new_state[in_pl] = list(
                    (Counter(new_state[in_pl]) - Counter(list(binding[0][1][ot]))).elements())
                if new_state[in_pl] == []:
                    del new_state[in_pl]
            state_update_pairs.append((new_state, update))

    else:
        possible = False
        for t in ocpn.transitions:
            if t.silent:
                if model_enabled(ocpn, state, t):
                    input_tokens = {ot: [] for ot in object_types}
                    input_token_combinations = {ot: [] for ot in object_types}
                    in_places = {}
                    out_places = {}
                    for ot in object_types:
                        in_places[ot] = [(x, y) for (x, y) in [(a.source, a.variable) for a in t.in_arcs] if
                                         x.object_type == ot]
                        out_places[ot] = [x for x in [
                            a.target for a in t.out_arcs] if x.object_type == ot]
                        token_lists = [[z for z in state[x]]
                                       for (x, y) in in_places[ot]]
                        if len(token_lists) != 0:
                            input_tokens[ot] = set.intersection(
                                *map(set, token_lists))
                            input_token_combinations[ot] = list(
                                combinations(input_tokens[ot], 1))
                        else:
                            input_tokens[ot] = set()
                    indices_list = [
                        list(range(len(input_token_combinations[ot]))) if len(input_token_combinations[ot]) != 0 else [
                            -1] for ot in object_types]
                    possible_combinations = list(product(*indices_list))
                    for comb in possible_combinations:
                        binding_silent = {}
                        for i in range(len(object_types)):
                            ot = object_types[i]
                            if -1 == comb[i]:
                                continue
                            binding_silent[ot] = input_token_combinations[ot][comb[i]]
                        new_state = {k: state[k].copy() for k in state.keys()}
                        update = not t.silent
                        for ot in object_types:
                            if ot not in binding_silent.keys():
                                continue
                            for out_pl in out_places[ot]:
                                if out_pl not in new_state.keys():
                                    new_state[out_pl] = []
                                new_state[out_pl] += list(binding_silent[ot])
                            for (in_pl, is_v) in in_places[ot]:
                                new_state[in_pl] = list(
                                    (Counter(new_state[in_pl]) - Counter(list(binding_silent[ot]))).elements())
                                if new_state[in_pl] == []:
                                    del new_state[in_pl]
                        state_update_pairs.append((new_state, update))
    return state_update_pairs, possible


def update_binding(binding, update):
    if update:
        return binding[1:]
    else:
        return binding


def enabled_log_activities(ocel, contexts):
    context_mapping = {}
    log_contexts = {}
    for index, event in ocel.log.iterrows():
        context = context_to_string(contexts[event["event_id"]])
        if context not in log_contexts.keys():
            log_contexts[context] = [index]
            context_mapping[context] = contexts[event["event_id"]]
        else:
            log_contexts[context].append(index)
    en_l = {}
    for context in log_contexts.keys():
        event_ids = log_contexts[context]
        en_l[context] = []
        for e in event_ids:
            en_l[context].append(ocel.log.at[e, "event_activity"])
        en_l[context] = list(set(en_l[context]))
    return en_l


def calculate_single_event(context, binding, object_types, ocpn):
    q = []
    state_binding_set = set()
    initial_node = [{}, binding]
    all_objects = {}
    for ot in object_types:
        all_objects[ot] = set()
        for b in binding:
            for o in b[1][ot]:
                all_objects[ot].add((ot, o))
    for color in context.keys():
        tokens = all_objects[color]
        to_be_added = 0
        if len(tokens) != len(list(context[color].elements())):
            to_be_added = len(list(context[color].elements())) - len(tokens)

        if tokens == set() and to_be_added == 0:
            continue
        for p in ocpn.places:
            if p.object_type == color and p.initial:
                # add START Tokens for each prefix a new token with new id
                initial_node[0][p] = []
                for (ot, o) in tokens:
                    initial_node[0][p].append((ot, o))
                for i in range(0, to_be_added):
                    initial_node[0][p].append((ot, "additional" + str(i)))

    initial_node = [initial_node]
    # transform bindings such that objects are identified as ot o not only o
    for b in binding:
        for ot in object_types:
            b[1][ot] = [(ot, o) for o in b[1][ot]]
    [q.append(node) for node in initial_node]
    index = 0
    context_string_target = context_to_string(context)
    result = (context_string_target, set())
    [state_binding_set.add(
        (state_to_place_counter(elem[0]), len(elem[1]))) for elem in q]
    times = [0, 0, 0, 0, 0]
    while not index == len(q):
        # For long running event calculations
        if index > 70000:
            print("Aborting: Timeout single event")
            break

        elem = q[index]
        index += 1
        ti = time.time()
        if len(elem[1]) == 0:
            for t in ocpn.transitions:
                if model_enabled(ocpn, elem[0], t) and not t.silent:
                    result[1].add(t.label)
        times[0] += time.time() - ti
        ti = time.time()
        state_update_pairs, binding_possible = calculate_next_states_on_bindings(
            ocpn, elem[0], elem[1], object_types)
        times[1] += time.time() - ti
        # for all next states
        # if the binding is possible, go to the end of the queue and append the next state there
        # This is an approximation technique
        # if binding_possible:
        #    index = len(q)
        for (state, update) in state_update_pairs:
            ti = time.time()
            updated_binding = update_binding(elem[1], update)
            times[2] += time.time() - ti
            ti = time.time()
            traditional_state_string = state_to_place_counter(state)
            times[3] += time.time() - ti
            ti = time.time()
            if (traditional_state_string, len(updated_binding)) in state_binding_set:
                continue
            state_binding_set.add(
                (traditional_state_string, len(updated_binding)))
            q.append([state, updated_binding])
            times[4] += time.time() - ti
            # this could be used to get a rough idea of the progress without any communication between processes
    # =============================================================================
    #     if random.randint(0, 500) == 1:
    #         print("500 events calculated")
    # =============================================================================
    return result, times


def enabled_model_activities_multiprocessing(contexts, bindings, ocpn, object_types):
    pool = ThreadPool(4)
    context_list = [contexts[i] for i in contexts.keys()]
    binding_list = [bindings[i] for i in contexts.keys()]
    result = pool.starmap(calculate_single_event,
                          zip(context_list, binding_list, itertools.repeat(object_types), itertools.repeat(ocpn)))
    results = {}
    total_times = numpy.array([0.0, 0.0, 0.0, 0.0, 0.0])
    for (k, v), times in result:
        total_times += numpy.array(times)
        if k not in results.keys():
            results[k] = set()
        [results[k].add(v_elem) for v_elem in v]
    return results


def calculate_precision_and_fitness(ocel, context_mapping, en_l, en_m):
    prec = []
    fit = []
    skipped = 0
    for index, row in ocel.log.iterrows():
        e_id = row["event_id"]
        context = context_mapping[e_id]
        en_l_a = en_l[context_to_string(context)]
        en_m_a = en_m[context_to_string(context)]
        if len(en_m[context_to_string(context)]) == 0 or (set(en_l_a).intersection(en_m_a) == set()):
            skipped += 1
            fit.append(0)
            continue
        prec.append(
            len(set(en_l[context_to_string(context)]).intersection(set(en_m[context_to_string(context)]))) / float(
                len(en_m[context_to_string(context)])))
        fit.append(
            len(set(en_l[context_to_string(context)]).intersection(set(en_m[context_to_string(context)]))) / float(
                len(en_l[context_to_string(context)])))
    if len(fit) == 0:
        return 0, skipped, 0
    if len(prec) == 0:
        return 0, skipped, sum(fit) / len(fit)
    return sum(prec) / len(prec), skipped, sum(fit) / len(fit)
