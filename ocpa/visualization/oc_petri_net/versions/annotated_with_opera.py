import uuid
import tempfile
from graphviz import Digraph
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

    if 'waiting_time' in parameters['measures']:
        p_waiting = True
    else:
        p_waiting = False
    if 'service_time' in parameters['measures']:
        p_service = True
    else:
        p_service = False
    if 'sojourn_time' in parameters['measures']:
        p_sojourn = True
    else:
        p_sojourn = False
    if 'synchronization_time' in parameters['measures']:
        p_sync = True
    else:
        p_sync = False
    if 'pooling_time' in parameters['measures']:
        p_pooling = True
    else:
        p_pooling = False
    if 'lagging_time' in parameters['measures']:
        p_lagging = True
    else:
        p_lagging = False
    if 'group_size' in parameters['measures']:
        p_group_size = True
    else:
        p_group_size = False
    if 'act_freq' in parameters['measures']:
        p_act_freq = True
    else:
        p_act_freq = False
    if 'arc_freq' in parameters['measures']:
        p_arc_freq = True
    else:
        p_arc_freq = False

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
        # if missing_token == True:
        #     pl_str = "p=%d r=%d\\nc=%d m=%d" % (
        #         diagnostics["place_fitness_per_trace"][pl.name]["p"], diagnostics["place_fitness_per_trace"][pl.name]["r"], diagnostics["place_fitness_per_trace"][pl.name]["c"], diagnostics["place_fitness_per_trace"][pl.name]["m"])
        #     pl_label += "\n %s" % (pl_str)

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
            tr_xlabel = "?"
            # tr_xlabel = "Performance of %s" % (tr.name)
            tr_label += f"\n {diagnostics[tr.name]['act_freq']}"

            # if p_group_size:
            #     tr_xlabel += f'\n {diagnostics[tr.name]["group_size_hist"]}'

            # if p_waiting:
            #     tr_xlabel += '<br/>'
            #     tr_xlabel += diagnostics[tr.name]['waiting_time']

            # if p_service:
            #     tr_xlabel += '<br/>'
            #     tr_xlabel += diagnostics[tr.name]['service_time']

            # if p_sojourn:
            #     tr_xlabel += '<br/>'
            #     tr_xlabel += diagnostics[tr.name]['sojourn_time']

            # if p_sync:
            #     tr_xlabel += '<br/>'
            #     tr_xlabel += diagnostics[tr.name]['synchronization_time']

            # if p_pooling:
            #     tr_xlabel += '<br/>'
            #     tr_xlabel += diagnostics[tr.name]['pooling_time']

            # if p_lagging:
            #     tr_xlabel += '<br/>'
            #     tr_xlabel += diagnostics[tr.name]['lagging_time']
            #     tr_xlabel += '<br/>'
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
        if arc.__repr__() in diagnostics["arc_freq"]:
            freq = diagnostics["arc_freq"][arc.__repr__()]
        else:
            freq = ""
        arc_annotation += f"{freq}"
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


def add_group_size(tr_name, agg, group_size):
    added_tr_xlabel = f"<br/> {agg} number of objects: "
    if agg in group_size[tr_name]:
        for obj_type in group_size[tr_name][agg].keys():
            added_tr_xlabel += "%s=%d " % (obj_type,
                                           group_size[tr_name][agg][obj_type])
    return added_tr_xlabel


def add_waiting_time(tr_name, agg, waiting_time):
    added_tr_xlabel = f"<br/> {agg} waiting time: "
    if tr_name in waiting_time and agg in waiting_time[tr_name]:
        added_tr_xlabel += "%s " % (waiting_time[tr_name][agg])
    return added_tr_xlabel


def add_service_time(tr_name, agg, service_time):
    added_tr_xlabel = f"<br/> {agg} service time: "
    if tr_name in service_time and agg in service_time[tr_name]:
        added_tr_xlabel += "%s " % (service_time[tr_name][agg])
    return added_tr_xlabel


def add_sojourn_time(tr_name, agg, sojourn_time):
    added_tr_xlabel = f"<br/> {agg} sojourn time: "
    if tr_name in sojourn_time and agg in sojourn_time[tr_name]:
        added_tr_xlabel += "%s " % (sojourn_time[tr_name][agg])
    return added_tr_xlabel


def add_synchronization_time(tr_name, agg, synchronization_time):
    added_tr_xlabel = f"<br/> {agg} synchronization time: "
    if tr_name in synchronization_time and agg in synchronization_time[tr_name]:
        added_tr_xlabel += "%s " % (synchronization_time[tr_name][agg])
    return added_tr_xlabel


def add_pooling_time(tr_name, ot, agg, pooling_time):
    added_tr_xlabel = f"<br/> {agg} pooling time: "
    if tr_name in pooling_time[ot] and agg in pooling_time[ot][tr_name]:
        added_tr_xlabel += "%s " % (pooling_time[ot][tr_name][agg])
    return added_tr_xlabel


def add_lagging_time(tr_name, ot, agg, lagging_time):
    added_tr_xlabel = f"<br/> {agg} lagging time: "
    if tr_name in lagging_time[ot] and agg in lagging_time[ot][tr_name]:
        added_tr_xlabel += "%s " % (lagging_time[ot][tr_name][agg])
    return added_tr_xlabel
