import time

import networkx as nx

import ocpa.algo.util.variants.versions.utils.helper as helper_functions


def apply(ocel, parameters):
    """
    Determining variants in the two-phase approach by calculating lexicographical respresentation of process executions
    and, subsequently, refining the calsses through one-to-one isomorphism comparisons. The exact calculation with
    refinement can be enforced through setting the parameters. Calling this method is usually integrated in the
    :class:`OCEL class <ocpa.objects.log.ocel.OCEL>` and
    is specified in the parameters usually set when importing the OCEL in
    :func:`CSV importer <ocpa.objects.log.importer.csv.factory.apply>`
    or :func:`JSONOCEL importer <ocpa.objects.log.importer.ocel.factory.apply>`
    or :func:`JSONXML importer <ocpa.objects.log.importer.ocel.factory.apply>`.

    :param ocel: Object-centric event log
    :type ocel: :class:`OCEL <ocpa.objects.log.ocel.OCEL>`
    :param parameters: Parameters for the method. Keys contain:
        - "timeout" in s for aborting variant calculation
        - "exact_variant_calculation" boolean for enforcing the refinement of initial classes (exact isomorphism
        calculation, initial classes might not be exact)
    :type parameters: : Dict
    :return: variants, v_freq_list, variant_graphs, variants_dict

    """
    timeout = parameters["timeout"] if "timeout" in parameters.keys() else 3600
    ocel.log.log["event_objects"] = ocel.log.log.apply(
        lambda x: [(ot, o) for ot in ocel.object_types for o in x[ot]], axis=1
    )
    variants_dict = dict()
    variants_graph_dict = dict()
    variant_graphs = dict()
    case_id = 0
    mapping_activity = dict(
        zip(ocel.log.log["event_id"], ocel.log.log["event_activity"])
    )
    mapping_objects = dict(zip(ocel.log.log["event_id"], ocel.log.log["event_objects"]))
    for v_g in ocel.process_executions:
        case = helper_functions.project_subgraph_on_activity(
            ocel,
            ocel.graph.eog.subgraph(v_g),
            case_id,
            mapping_objects,
            mapping_activity,
        )
        variant = nx.weisfeiler_lehman_graph_hash(
            case, node_attr="label", edge_attr="type"
        )
        variant_string = variant
        if variant_string not in variants_dict:
            variants_dict[variant_string] = []
            variants_graph_dict[variant_string] = []
            variant_graphs[variant_string] = (
                case,
                ocel.process_execution_objects[case_id],
            )  # EOG.subgraph(v_g)#case
        variants_dict[variant_string].append(case_id)
        variants_graph_dict[variant_string].append(case)
        case_id += 1

    start_time = time.time()
    if (
        parameters["exact_variant_calculation"]
        if "exact_variant_calculation" in parameters.keys()
        else False
    ):
        for _class in variants_graph_dict.keys():
            subclass_counter = 0
            subclass_mappings = {}

            for j in range(0, len(variants_graph_dict[_class])):
                exec = variants_graph_dict[_class][j]
                case_id = variants_dict[_class][j]
                found = False
                for i in range(1, subclass_counter + 1):
                    if nx.is_isomorphic(
                        exec,
                        subclass_mappings[i][0][0],
                        node_match=lambda x, y: x["label"] == y["label"],
                        edge_match=lambda x, y: x["type"] == y["type"],
                    ):
                        subclass_mappings[subclass_counter].append((exec, case_id))
                        found = True
                        break
                if found:
                    continue
                subclass_counter += 1
                subclass_mappings[subclass_counter] = [(exec, case_id)]
                if (time.time() - start_time) > timeout:
                    raise Exception("timeout")
            for ind in subclass_mappings.keys():
                variants_dict[_class + str(ind)] = [
                    case_id for (exec, case_id) in subclass_mappings[ind]
                ]
                (exec, case_id) = subclass_mappings[ind][0]
                variant_graphs[_class + str(ind)] = (
                    exec,
                    ocel.process_execution_objects[case_id],
                )
            del variants_dict[_class]
            del variant_graphs[_class]

    variant_frequencies = {
        v: len(variants_dict[v]) / len(ocel.process_executions)
        for v in variants_dict.keys()
    }
    variants, v_freq_list = map(
        list,
        zip(
            *sorted(list(variant_frequencies.items()), key=lambda x: x[1], reverse=True)
        ),
    )
    variant_event_map = {}
    for v_id in range(0, len(variants)):
        v = variants[v_id]
        cases = [ocel.process_executions[c_id] for c_id in variants_dict[v]]
        events = set().union(*cases)
        for e in events:
            if e not in variant_event_map.keys():
                variant_event_map[e] = []
            variant_event_map[e] += [v_id]
    ocel.log.log["event_variant"] = ocel.log.log["event_id"].map(variant_event_map)
    ocel.log.log.drop("event_objects", axis=1, inplace=True)
    return variants, v_freq_list, variant_graphs, variants_dict
