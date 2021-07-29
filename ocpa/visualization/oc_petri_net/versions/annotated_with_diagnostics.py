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

    act_count = diagnostics["replayed_act_freq"]
    replayed_performance_min = diagnostics["replayed_performance_min"]
    replayed_performance_median = diagnostics[
        "replayed_performance_median"]
    replayed_performance_mean = diagnostics["replayed_performance_mean"]
    replayed_performance_max = diagnostics["replayed_performance_max"]

    agg_merged_group_size_hist = diagnostics["agg_merged_group_size_hist"]

    replayed_place_fitness = diagnostics["replayed_place_fitness"]

    replayed_arc_frequency = diagnostics["replayed_arc_frequency"]

    if 'act_count' in parameters:
        d_act_freq = parameters['act_count']
    else:
        d_act_freq = False

    if 'max_group_size' in parameters:
        d_max_group_size = parameters['max_group_size']
    else:
        d_max_group_size = False

    if 'min_group_size' in parameters:
        d_min_group_size = parameters['min_group_size']
    else:
        d_min_group_size = False

    if 'mean_group_size' in parameters:
        d_mean_group_size = parameters['mean_group_size']
    else:
        d_mean_group_size = False

    if 'median_group_size' in parameters:
        d_median_group_size = parameters['median_group_size']
    else:
        d_median_group_size = False

    if 'produced_token' in parameters:
        d_produced_token = parameters['produced_token']
    else:
        d_produced_token = False

    if 'consumed_token' in parameters:
        d_consumed_token = parameters['consumed_token']
    else:
        d_consumed_token = False

    if 'missing_token' in parameters:
        d_missing_token = parameters['missing_token']
    else:
        d_missing_token = False

    if 'remaining_token' in parameters:
        d_remaining_token = parameters['remaining_token']
    else:
        d_remaining_token = False

    if 'arc_freq' in parameters:
        d_arc_freq = parameters['arc_freq']
    else:
        d_arc_freq = False

    if 'avg_sojourn_time' in parameters:
        d_avg_sojourn_time = parameters['avg_sojourn_time']
    else:
        d_avg_sojourn_time = False

    if 'med_sojourn_time' in parameters:
        d_med_sojourn_time = parameters['med_sojourn_time']
    else:
        d_med_sojourn_time = False

    if 'min_sojourn_time' in parameters:
        d_min_sojourn_time = parameters['min_sojourn_time']
    else:
        d_min_sojourn_time = False

    if 'max_sojourn_time' in parameters:
        d_max_sojourn_time = parameters['max_sojourn_time']
    else:
        d_max_sojourn_time = False

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

        pl_label = pl.name
        if d_missing_token == True:
            pl_str = "p=%d r=%d\\nc=%d m=%d" % (
                replayed_place_fitness[pl.name]["p"], replayed_place_fitness[pl.name]["r"], replayed_place_fitness[pl.name]["c"], replayed_place_fitness[pl.name]["m"])
            pl_label += "\n %s" % (pl_str)

        if pl.initial == True:
            g.node("(p)%s" % (pl.name), pl.name, shape="circle", style="filled", fillcolor=color, color=color,
                   fontsize="13.0", labelfontsize="13.0")
        elif pl.final == True:
            g.node("(p)%s" % (pl.name), pl.name, shape="circle", style="filled", color=color, fillcolor=color,
                   fontsize="13.0", labelfontsize="13.0")
        else:
            g.node("(p)%s" % (pl.name), pl_label, shape="circle", color=color,
                   fontsize="13.0", labelfontsize="13.0")
        all_objs[pl] = "(p)%s" % (pl.name)

    for tr in ocpn.transitions:
        # this_uuid = str(uuid.uuid4())
        this_uuid = "t%d" % (tr_count)
        tr_count += 1
        if tr.silent == True:
            g.node(this_uuid, this_uuid, fontcolor="#FFFFFF", shape="box",
                   fillcolor="#000000", style="filled", labelfontsize="18.0")
            all_objs[tr] = this_uuid
        elif tr.name not in trans_names:
            tr_label = tr.name
            tr_xlabel = "-"
            if d_act_freq == True:
                tr_label += "\n (%d)" % (act_count[tr.name])

            if d_max_group_size == True:
                tr_xlabel += "\n max: "
                for obj_type in agg_merged_group_size_hist[tr.name]["max"].keys():
                    tr_xlabel += "%s=%d " % (obj_type,
                                             agg_merged_group_size_hist[tr.name]["max"][obj_type])

            if d_min_group_size == True:
                tr_xlabel += "\n min: "
                for obj_type in agg_merged_group_size_hist[tr.name]["min"].keys():
                    tr_xlabel += "%s=%d " % (obj_type,
                                             agg_merged_group_size_hist[tr.name]["min"][obj_type])

            if d_mean_group_size == True:
                tr_xlabel += "\n mean: "
                for obj_type in agg_merged_group_size_hist[tr.name]["mean"].keys():
                    tr_xlabel += "%s=%d " % (
                        obj_type, agg_merged_group_size_hist[tr.name]["mean"][obj_type])

            if d_median_group_size == True:
                tr_xlabel += "\n median: "
                for obj_type in agg_merged_group_size_hist[tr.name]["median"].keys():
                    tr_xlabel += "%s=%d " % (
                        obj_type, agg_merged_group_size_hist[tr.name]["median"][obj_type])
            g.node("(t)%s" % (tr.name), "%s" % (tr_label), shape="box", fontsize="36.0",
                   labelfontsize="36.0", xlabel='''<<FONT POINT-SIZE="11">%s</FONT>>''' % (tr_xlabel))
            trans_names[tr.name] = tr.name
            all_objs[tr] = "(t)%s" % (tr.name)
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

        if d_max_sojourn_time == True:
            if repr(arc) in replayed_performance_max.keys():
                arc_annotation += "\n max. sojourn time=%s" % (
                    replayed_performance_max[repr(arc)])

        if d_avg_sojourn_time == True:
            if repr(arc) in replayed_performance_mean.keys():
                arc_annotation += "\n avg. sojourn time=%s" % (
                    replayed_performance_mean[repr(arc)])

        if d_med_sojourn_time == True:
            if repr(arc) in replayed_performance_median.keys():
                arc_annotation += "\n med. sojourn time=%s" % (
                    replayed_performance_median[repr(arc)])

        if d_min_sojourn_time == True:
            if repr(arc) in replayed_performance_min.keys():
                arc_annotation += "\n min. sojourn time=%s" % (
                    replayed_performance_min[repr(arc)])

        penwidth = "1"
        if d_arc_freq == True:
            arc_freq = replayed_arc_frequency[arc.__repr__()]
            arc_annotation += "\n freq=%s" % (arc_freq)
        if arc.variable == True:
            g.edge(all_objs[source_node], all_objs[target_node],
                   label=arc_annotation, color=color + ":white:" + color, fontsize="13.0", penwidth=penwidth)
        else:
            g.edge(all_objs[source_node], all_objs[target_node],
                   label=arc_annotation, color=color, fontsize="13.0", penwidth=penwidth)

        all_objs[arc] = this_uuid

    g.attr(overlap='false')
    g.attr(fontsize='11')

    g.format = image_format
    return g
