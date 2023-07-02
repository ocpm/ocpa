import uuid
import tempfile
from graphviz import Digraph
from ocpa.objects.oc_petri_net.obj import ObjectCentricPetriNet
from ocpa.visualization.oc_petri_net.util.util import equal_arc
from statistics import median, mean

COLORS = ['#7f66ff',
          '#ff3399',
          '#f58b55',
          '#f25e65',
          '#261926',
          '#ddb14d',
          '#5387d5',
          '#1c3474',
          '#a37554',
          '#8bc34a',
          '#cddc39',
          '#ffeb3b',
          '#ffc107',
          '#ff9800',
          '#ff5722',
          '#795548',
          '#9e9e9e',
          '#607d8b',
          '#9affff',
          '#000000']


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
    color_mapping = dict()
    object_types = ocpn.object_types
    for index, ot in enumerate(object_types):
        color_mapping[ot] = COLORS[index % len(COLORS)]

    for pl in ocpn.places:
        this_uuid = str(uuid.uuid4())
        color = color_mapping[pl.object_type]
        pl_label = pl.name

        if pl.initial == True or pl.final == True:
            g.node(this_uuid, pl_label, shape="circle", style="filled", fillcolor=color, color=color,
                   fontsize="13.0", labelfontsize="13.0")
        else:
            g.node(this_uuid, pl_label, shape="circle", color=color,
                   fontsize="13.0", labelfontsize="13.0")
        all_objs[pl] = this_uuid

    for tr in ocpn.transitions:
        this_uuid = str(uuid.uuid4())
        tr_label = tr.label

        if tr.silent == True:
            g.node(this_uuid, "", fontcolor="#FFFFFF", shape="box",
                   fillcolor="#000000", style="filled", labelfontsize="18.0")
            all_objs[tr] = this_uuid
        else:
            tr_label = tr.label
            tr_label += f"<br/><FONT POINT-SIZE='36'>{diagnostics[tr.label]['act_freq']}</FONT>"
            tr_xlabel = ""
            for chosen_measure in diagnostics[tr.label].keys():
                tr_xlabel += add_diagnostics(diagnostics[tr.label][chosen_measure], chosen_measure)
            tr_label += f"<br/><FONT POINT-SIZE='15'>{tr_xlabel}</FONT>"
            g.node(this_uuid, "<%s>" % tr_label, shape="box", fontsize="36.0", labelfontsize="36.0")

            all_objs[tr] = this_uuid

    for arc in ocpn.arcs:
        this_uuid = str(uuid.uuid4())
        arc_annotation = ""

        source_node = arc.source
        target_node = arc.target

        if type(source_node) == ObjectCentricPetriNet.Place:
            color = color_mapping[source_node.object_type]
        elif type(target_node) == ObjectCentricPetriNet.Place:
            color = color_mapping[target_node.object_type]

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
    g.attr(ranksep='1')
    g.attr(nodesep='1')

    g.format = image_format
    return g

def add_diagnostics(tr_diagnostics, performance_measure):
    printed_diagnostics = ""
    if performance_measure in ['waiting_time', 'service_time', 'sojourn_time', 'synchronization_time', 'object_count', 'flow_time']:
        for agg in tr_diagnostics.keys():
            printed_diagnostics += f'{agg} {performance_measure}: {tr_diagnostics[agg]}<br/>'
    elif performance_measure in ['pooling_time', 'lagging_time']:
        for obj_type in tr_diagnostics.keys():
            for agg in tr_diagnostics[obj_type].keys():
                printed_diagnostics += f'{agg} {performance_measure} of {obj_type}: {tr_diagnostics[obj_type][agg]}<br/>'
    return printed_diagnostics
