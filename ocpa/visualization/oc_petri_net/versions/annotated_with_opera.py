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
    agg_merged_group_size_hist = diagnostics["agg_merged_group_size_hist"]
    replayed_place_fitness = diagnostics["replayed_place_fitness"]
    replayed_arc_frequency = diagnostics["replayed_arc_frequency"]

    agg_waiting_time = diagnostics["agg_waiting_time"]
    agg_service_time = diagnostics["agg_service_time"]
    agg_sojourn_time = diagnostics["agg_sojourn_time"]
    agg_synchronization_time = diagnostics["agg_synchronization_time"]

    if 'act_freq' in parameters:
        act_freq = parameters['act_freq']
    else:
        act_freq = False

    if 'max_group_size' in parameters:
        max_group_size = parameters['max_group_size']
    else:
        max_group_size = False

    if 'min_group_size' in parameters:
        min_group_size = parameters['min_group_size']
    else:
        min_group_size = False

    if 'mean_group_size' in parameters:
        mean_group_size = parameters['mean_group_size']
    else:
        mean_group_size = False

    if 'median_group_size' in parameters:
        median_group_size = parameters['median_group_size']
    else:
        median_group_size = False

    if 'produced_token' in parameters:
        produced_token = parameters['produced_token']
    else:
        produced_token = False

    if 'consumed_token' in parameters:
        consumed_token = parameters['consumed_token']
    else:
        consumed_token = False

    if 'missing_token' in parameters:
        missing_token = parameters['missing_token']
    else:
        missing_token = False

    if 'remaining_token' in parameters:
        remaining_token = parameters['remaining_token']
    else:
        remaining_token = False

    if 'arc_freq' in parameters:
        arc_freq = parameters['arc_freq']
    else:
        arc_freq = False

    if 'mean_waiting_time' in parameters:
        mean_waiting_time = parameters['mean_waiting_time']
    else:
        mean_waiting_time = False

    if 'median_waiting_time' in parameters:
        median_waiting_time = parameters['median_waiting_time']
    else:
        median_waiting_time = False

    if 'min_waiting_time' in parameters:
        min_waiting_time = parameters['min_waiting_time']
    else:
        min_waiting_time = False

    if 'max_waiting_time' in parameters:
        max_waiting_time = parameters['max_waiting_time']
    else:
        max_waiting_time = False

    if 'stdev_waiting_time' in parameters:
        stdev_waiting_time = parameters['stdev_waiting_time']
    else:
        stdev_waiting_time = False

    if 'mean_service_time' in parameters:
        mean_service_time = parameters['mean_service_time']
    else:
        mean_service_time = False

    if 'median_service_time' in parameters:
        median_service_time = parameters['median_service_time']
    else:
        median_service_time = False

    if 'min_service_time' in parameters:
        min_service_time = parameters['min_service_time']
    else:
        min_service_time = False

    if 'max_service_time' in parameters:
        max_service_time = parameters['max_service_time']
    else:
        max_service_time = False

    if 'stdev_service_time' in parameters:
        stdev_service_time = parameters['stdev_service_time']
    else:
        stdev_service_time = False

    if 'mean_sojourn_time' in parameters:
        mean_sojourn_time = parameters['mean_sojourn_time']
    else:
        mean_sojourn_time = False

    if 'median_sojourn_time' in parameters:
        median_sojourn_time = parameters['median_sojourn_time']
    else:
        median_sojourn_time = False

    if 'min_sojourn_time' in parameters:
        min_sojourn_time = parameters['min_sojourn_time']
    else:
        min_sojourn_time = False

    if 'max_sojourn_time' in parameters:
        max_sojourn_time = parameters['max_sojourn_time']
    else:
        max_sojourn_time = False

    if 'stdev_sojourn_time' in parameters:
        stdev_sojourn_time = parameters['stdev_sojourn_time']
    else:
        stdev_sojourn_time = False

    if 'mean_synchronization_time' in parameters:
        mean_synchronization_time = parameters['mean_synchronization_time']
    else:
        mean_synchronization_time = False

    if 'median_synchronization_time' in parameters:
        median_synchronization_time = parameters['median_synchronization_time']
    else:
        median_synchronization_time = False

    if 'min_synchronization_time' in parameters:
        min_synchronization_time = parameters['min_synchronization_time']
    else:
        min_synchronization_time = False

    if 'max_synchronization_time' in parameters:
        max_synchronization_time = parameters['max_synchronization_time']
    else:
        max_synchronization_time = False

    if 'stdev_synchronization_time' in parameters:
        stdev_synchronization_time = parameters['stdev_synchronization_time']
    else:
        stdev_synchronization_time = False

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
        if missing_token == True:
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
            tr_xlabel = "Performance of %s" % (tr.name)
            if act_freq == True:
                tr_label += "\n (%d)" % (act_count[tr.name])

            if max_group_size == True:
                tr_xlabel += "<br/> max. number of objects: "
                for obj_type in agg_merged_group_size_hist[tr.name]["max"].keys():
                    tr_xlabel += "%s=%d " % (obj_type,
                                             agg_merged_group_size_hist[tr.name]["max"][obj_type])

            if min_group_size == True:
                tr_xlabel += "<br/> min. number of objects: "
                for obj_type in agg_merged_group_size_hist[tr.name]["min"].keys():
                    tr_xlabel += "%s=%d " % (obj_type,
                                             agg_merged_group_size_hist[tr.name]["min"][obj_type])

            if mean_group_size == True:
                tr_xlabel += "<br/> mean number of objects: "
                for obj_type in agg_merged_group_size_hist[tr.name]["mean"].keys():
                    tr_xlabel += "%s=%d " % (
                        obj_type, agg_merged_group_size_hist[tr.name]["mean"][obj_type])

            if median_group_size == True:
                tr_xlabel += "<br/> median number of objects: "
                for obj_type in agg_merged_group_size_hist[tr.name]["median"].keys():
                    tr_xlabel += "%s=%d " % (
                        obj_type, agg_merged_group_size_hist[tr.name]["median"][obj_type])
            if mean_waiting_time == True:
                tr_xlabel += "<br/> mean waiting time: "
                if tr.name in agg_waiting_time:
                    tr_xlabel += "%s " % (agg_waiting_time[tr.name]["mean"])
            if median_waiting_time == True:
                tr_xlabel += "<br/> median waiting time: "
                if tr.name in agg_waiting_time:
                    tr_xlabel += "%s " % (agg_waiting_time[tr.name]["median"])
            if min_waiting_time == True:
                tr_xlabel += "<br/> min. waiting time: "
                if tr.name in agg_waiting_time:
                    tr_xlabel += "%s " % (agg_waiting_time[tr.name]["min"])
            if max_waiting_time == True:
                tr_xlabel += "<br/> max. waiting time: "
                if tr.name in agg_waiting_time:
                    tr_xlabel += "%s " % (agg_waiting_time[tr.name]["max"])
            if stdev_waiting_time == True:
                tr_xlabel += "<br/> stdev. waiting time: "
                if tr.name in agg_waiting_time:
                    tr_xlabel += "%s " % (agg_waiting_time[tr.name]["stdev"])

            if mean_service_time == True:
                tr_xlabel += "<br/> mean service time: "
                if tr.name in agg_service_time:
                    tr_xlabel += "%s " % (agg_service_time[tr.name]["mean"])
            if median_service_time == True:
                tr_xlabel += "<br/> median service time: "
                if tr.name in agg_service_time:
                    tr_xlabel += "%s " % (agg_service_time[tr.name]["median"])
            if min_service_time == True:
                tr_xlabel += "<br/> min. service time: "
                if tr.name in agg_service_time:
                    tr_xlabel += "%s " % (agg_service_time[tr.name]["min"])
            if max_service_time == True:
                tr_xlabel += "<br/> max. service time: "
                if tr.name in agg_service_time:
                    tr_xlabel += "%s " % (agg_service_time[tr.name]["max"])
            if stdev_service_time == True:
                tr_xlabel += "<br/> stdev. service time: "
                if tr.name in agg_service_time:
                    tr_xlabel += "%s " % (agg_service_time[tr.name]["stdev"])

            if mean_sojourn_time == True:
                tr_xlabel += "<br/> mean sojourn time: "
                if tr.name in agg_sojourn_time:
                    tr_xlabel += "%s " % (agg_sojourn_time[tr.name]["mean"])
            if median_sojourn_time == True:
                tr_xlabel += "<br/> median sojourn time: "
                if tr.name in agg_sojourn_time:
                    tr_xlabel += "%s " % (agg_sojourn_time[tr.name]["median"])
            if min_sojourn_time == True:
                tr_xlabel += "<br/> min. sojourn time: "
                if tr.name in agg_sojourn_time:
                    tr_xlabel += "%s " % (agg_sojourn_time[tr.name]["min"])
            if max_sojourn_time == True:
                tr_xlabel += "<br/> max. sojourn time: "
                if tr.name in agg_sojourn_time:
                    tr_xlabel += "%s " % (agg_sojourn_time[tr.name]["max"])
            if stdev_sojourn_time == True:
                tr_xlabel += "<br/> stdev. sojourn time: "
                if tr.name in agg_sojourn_time:
                    tr_xlabel += "%s " % (agg_sojourn_time[tr.name]["stdev"])

            if mean_synchronization_time == True:
                tr_xlabel += "<br/> mean synchronization time: "
                if tr.name in agg_synchronization_time:
                    tr_xlabel += "%s " % (
                        agg_synchronization_time[tr.name]["mean"])
            if median_synchronization_time == True:
                tr_xlabel += "<br/> median synchronization time: "
                if tr.name in agg_synchronization_time:
                    tr_xlabel += "%s " % (
                        agg_synchronization_time[tr.name]["median"])
            if min_synchronization_time == True:
                tr_xlabel += "<br/> min. synchronization time: "
                if tr.name in agg_synchronization_time:
                    tr_xlabel += "%s " % (
                        agg_synchronization_time[tr.name]["min"])
            if max_synchronization_time == True:
                tr_xlabel += "<br/> max. synchronization time: "
                if tr.name in agg_synchronization_time:
                    tr_xlabel += "%s " % (
                        agg_synchronization_time[tr.name]["max"])
            if stdev_synchronization_time == True:
                tr_xlabel += "<br/> stdev. synchronization time: "
                if tr.name in agg_synchronization_time:
                    tr_xlabel += "%s " % (
                        agg_synchronization_time[tr.name]["stdev"])

            # g.node("(t)%s" % (tr.name), "%s" % (tr_label), shape="box", fontsize="36.0",
            #        labelfontsize="36.0", xlabel='''<<FONT POINT-SIZE="11">%s</FONT>>''' % (tr_xlabel))
            g.node("(t)%s" % (tr.name), "%s" % (tr_label), shape="box", fontsize="36.0",
                   labelfontsize="36.0", xlabel='''<<FONT POINT-SIZE="5">%s</FONT>>''' % (tr_xlabel))
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

        penwidth = "1"
        if arc_freq == True:
            freq = replayed_arc_frequency[arc.__repr__()]
            arc_annotation += "\n freq=%s" % (freq)
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
