import uuid
import tempfile
from graphviz import Digraph
from pm4py.objects.petri.petrinet import PetriNet
from ocpa.objects.oc_petri_net.obj import ObjectCentricPetriNet
from ocpa.visualization.oc_petri_net.util.util import equal_arc
from statistics import median, mean

COLORS = ["#05B202", "#A13CCD", "#BA0D39", "#39F6C0", "#E90638", "#07B423", "#306A8A", "#678225", "#2742FE", "#4C9A75",
          "#4C36E9", "#7DB022", "#EDAC54", "#EAC439", "#EAC439", "#1A9C45", "#8A51C4", "#496A63", "#FB9543", "#2B49DD",
          "#13ADA5", "#2DD8C1", "#2E53D7", "#EF9B77", "#06924F", "#AC2C4D", "#82193F", "#0140D3"]


def apply(ocpn, diagnostics, parameters=None):
    if parameters is None:
        parameters = {}

    image_format = "png"
    if "format" in parameters:
        image_format = parameters["format"]

    filename = tempfile.NamedTemporaryFile(suffix='.gv').name
    g = Digraph("", filename=filename, engine='dot',
                graph_attr={'bgcolor': 'transparent'})

    all_objs = {}
    trans_names = {}

    replay = diagnostics["replay"]
    act_count = diagnostics["act_count"]
    place_fitness_per_trace_persp = diagnostics["place_fitness_per_trace"]
    group_size_hist_persp = diagnostics["group_size_hist"]
    aggregated_statistics_performance_min = diagnostics["aggregated_statistics_performance_min"]
    aggregated_statistics_performance_median = diagnostics[
        "aggregated_statistics_performance_median"]
    aggregated_statistics_performance_mean = diagnostics["aggregated_statistics_performance_mean"]
    aggregated_statistics_performance_mean = diagnostics["aggregated_statistics_performance_mean"]

    pl_count = 1
    tr_count = 1
    arc_count = 1

    # color = COLORS[index % len(COLORS)]
    color = "#05B202"
    color_mapping = dict()
    object_types = ocpn.object_types
    for index, ot in enumerate(object_types):
        color_mapping[ot] = COLORS[index % len(COLORS)]

    for pl in ocpn.places:
        # this_uuid = str(uuid.uuid4())
        this_uuid = "p%d" % (pl_count)
        # pl_str = this_uuid
        pl_count += 1
        color = color_mapping[pl.object_type]
        if pl.initial == True:
            g.node(pl.name, pl.name, shape="circle", style="filled", fillcolor=color, color=color,
                   fontsize="13.0", labelfontsize="13.0")
        elif pl.final == True:
            g.node(pl.name, pl.name, shape="circle", style="filled", color=color, fillcolor=color,
                   fontsize="13.0", labelfontsize="13.0")
        else:
            g.node(pl.name, pl.name, shape="circle", color=color,
                   fontsize="13.0", labelfontsize="13.0")
        all_objs[pl] = pl.name

    for tr in ocpn.transitions:
        # this_uuid = str(uuid.uuid4())
        this_uuid = "t%d" % (tr_count)
        tr_count += 1
        if tr.silent == True:
            g.node(this_uuid, this_uuid, fontcolor="#FFFFFF", shape="box",
                   fillcolor="#000000", style="filled", labelfontsize="18.0")
            all_objs[tr] = this_uuid
        elif tr.name not in trans_names:
            act_count_string = ""
            for obj_type in object_types:
                if obj_type in act_count:
                    if tr.name in act_count[obj_type]:
                        obj_count = act_count[obj_type][tr.name]
                        act_count_string += "%s:%s \n" % (str(obj_type),
                                                          str(obj_count))

            g.node(tr.name, "%s" % (tr.name), shape="box", fontsize="36.0",
                   labelfontsize="36.0", xlabel='''<<font POINT-SIZE="13">%s</font>>''' % (act_count_string))
            trans_names[tr.name] = tr.name
            all_objs[tr] = tr.name
        else:
            all_objs[tr] = trans_names[tr.name]

    for arc in ocpn.arcs:
        # this_uuid = str(uuid.uuid4())
        this_uuid = "a%d" % (arc_count)
        arc_count += 1
        arc_annotation = ""

        source_node = arc.source
        target_node = arc.target

        if type(source_node) == ObjectCentricPetriNet.Place:
            object_type = source_node.object_type
        elif type(target_node) == ObjectCentricPetriNet.Place:
            object_type = target_node.object_type

        color = color_mapping[object_type]

        for k in aggregated_statistics_performance_mean[object_type].keys():
            if equal_arc(k, arc):
                arc_annotation += "\\nperf: median=%s mean=%s" % (
                    aggregated_statistics_performance_median[object_type][k]['label'],
                    aggregated_statistics_performance_mean[object_type][k]['label'])
                break

        if arc.variable == True:
            g.edge(all_objs[source_node], all_objs[target_node],
                   label=arc_annotation, color=color + ":white:" + color, fontsize="13.0")
        else:
            g.edge(all_objs[source_node], all_objs[target_node],
                   label=arc_annotation, color=color, fontsize="13.0")

        all_objs[arc] = this_uuid

    g.attr(overlap='false')
    g.attr(fontsize='11')

    g.format = image_format
    return g


def apply2(ocpn, parameters=None):
    if parameters is None:
        parameters = {}

    image_format = "png"
    if "format" in parameters:
        image_format = parameters["format"]

    filename = tempfile.NamedTemporaryFile(suffix='.gv').name
    g = Digraph("", filename=filename, engine='dot',
                graph_attr={'bgcolor': 'transparent'})

    nets = ocpn["nets"]
    replay = ocpn["replay"]
    act_count = ocpn["act_count"]
    place_fitness_per_trace_persp = ocpn["place_fitness_per_trace"]
    group_size_hist_persp = ocpn["group_size_hist"]
    aggregated_statistics_performance_min = ocpn["aggregated_statistics_performance_min"]
    aggregated_statistics_performance_median = ocpn["aggregated_statistics_performance_median"]
    aggregated_statistics_performance_mean = ocpn["aggregated_statistics_performance_mean"]

    all_objs = {}
    trans_names = {}

    for index, persp in enumerate(nets):
        orig_act_count = {}

        color = COLORS[index % len(COLORS)]
        net, im, fm = nets[persp]
        rr = replay[persp]
        ac = act_count[persp]

        ag_perf_min = aggregated_statistics_performance_min[persp]
        ag_perf_median = aggregated_statistics_performance_median[persp]
        ag_perf_mean = aggregated_statistics_performance_mean[persp]
        place_fitness_per_trace = place_fitness_per_trace_persp[persp]
        group_size_hist = group_size_hist_persp[persp]

        for pl in net.places:
            this_uuid = str(uuid.uuid4())
            pl_str = "p=%d r=%d\\nc=%d m=%d" % (
                place_fitness_per_trace[pl]["p"], place_fitness_per_trace[pl]["r"], place_fitness_per_trace[pl]["c"],
                place_fitness_per_trace[pl]["m"])
            is_double_circled = False
            for arc in pl.in_arcs:
                if arc.source.label in group_size_hist:
                    if len(group_size_hist[arc.source.label]) != sum(group_size_hist[arc.source.label]):
                        is_double_circled = True
            for arc in pl.out_arcs:
                if arc.target.label in group_size_hist:
                    if len(group_size_hist[arc.target.label]) != sum(group_size_hist[arc.target.label]):
                        is_double_circled = True
            if is_double_circled:
                if pl in im:
                    g.node(pl.name, pl_str, shape="doublecircle", style="filled", color=color, fillcolor=color,
                           fontsize="13.0", labelfontsize="13.0", penwidth="3.0")
                elif pl in fm:
                    g.node(pl.name, pl_str, shape="doublecircle", style="filled", color=color, fillcolor=color,
                           fontsize="13.0", labelfontsize="13.0", penwidth="3.0")
                else:
                    g.node(pl.name, pl_str, shape="doublecircle", color=color,
                           fontsize="13.0", labelfontsize="13.0", penwidth="3.0")
            else:
                if pl in im:
                    g.node(pl.name, pl_str, shape="circle", style="filled", fillcolor=color, color=color,
                           fontsize="13.0", labelfontsize="13.0")
                elif pl in fm:
                    g.node(pl.name, pl_str, shape="circle", style="filled", color=color, fillcolor=color,
                           fontsize="13.0", labelfontsize="13.0")
                else:
                    g.node(pl.name, pl_str, shape="circle",
                           color=color, fontsize="13.0", labelfontsize="13.0")
            all_objs[pl] = pl.name

        for tr in net.transitions:
            this_uuid = str(uuid.uuid4())
            if tr.label is None:
                g.node(this_uuid, "", shape="box",
                       fillcolor="#000000", style="filled")
                all_objs[tr] = this_uuid
            elif tr.label not in trans_names:
                count = rr[tr]["label"].split("(")[-1].split("]")[0]
                orig_act_count[tr] = count
                this_act_count = "%d" % (float(ac[tr.label]))
                g.node(this_uuid, tr.label + " \\n" + this_act_count + "", shape="box", fontsize="36.0",
                       labelfontsize="36.0")
                trans_names[tr.label] = this_uuid
                all_objs[tr] = this_uuid
            else:
                all_objs[tr] = trans_names[tr.label]

        for arc in net.arcs:
            this_uuid = str(uuid.uuid4())

            source_node = arc.source
            target_node = arc.target
            to_double_arc = False

            if arc in rr:

                arc_count = float(rr[arc]['label'])

                if arc in ag_perf_min:
                    perf_str = "\\nperf: median=%s mean=%s" % (
                        ag_perf_median[arc]['label'],
                        ag_perf_mean[arc]['label'])
                else:
                    perf_str = ""

                if type(source_node) is PetriNet.Place:
                    if target_node.label in group_size_hist and max(group_size_hist[target_node.label]) > 1:
                        pre = "freq: median=%d mean=%.2f\\neve=%d uniqobj=%d\\n" % (
                            median(group_size_hist[target_node.label]), mean(
                                group_size_hist[target_node.label]),
                            len(group_size_hist[target_node.label]), sum(group_size_hist[target_node.label]))
                    else:
                        pre = "uniqobj=" + str(int(arc_count))
                    if target_node.label in group_size_hist and sum(group_size_hist[target_node.label]) != len(
                            group_size_hist[target_node.label]):
                        to_double_arc = True

                    ratio = pre + perf_str + ""

                else:
                    if source_node.label in group_size_hist and max(group_size_hist[source_node.label]) > 1:
                        pre = "freq: median=%d mean=%.2f\\neve=%d uniqobj=%d\\n" % (
                            median(group_size_hist[source_node.label]), mean(
                                group_size_hist[source_node.label]),
                            len(group_size_hist[source_node.label]), sum(group_size_hist[source_node.label]))
                    else:
                        pre = "uniqobj=" + str(int(arc_count))
                    if source_node.label in group_size_hist and sum(group_size_hist[source_node.label]) != len(
                            group_size_hist[source_node.label]):
                        to_double_arc = True

                    ratio = pre + perf_str + ""

                if to_double_arc:
                    g.edge(all_objs[source_node], all_objs[target_node], label=ratio, penwidth=str(3.0*float(rr[arc]['penwidth'])),
                           color=color + ":white:" + color, fontsize="13.0")
                else:
                    g.edge(all_objs[source_node], all_objs[target_node], label=ratio, penwidth=str(1.2*float(rr[arc]['penwidth'])),
                           color=color, fontsize="13.0")

                all_objs[arc] = this_uuid
            else:
                g.edge(all_objs[source_node], all_objs[target_node],
                       label="", color=color, fontsize="11.0")

    g.attr(overlap='false')
    g.attr(fontsize='11')

    g.format = image_format

    return g
