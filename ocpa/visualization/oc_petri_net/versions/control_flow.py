import uuid
import tempfile
from graphviz import Digraph
from ocpa.objects.oc_petri_net.obj import ObjectCentricPetriNet

# COLORS = ["#05B202", "#A13CCD", "#BA0D39", "#39F6C0", "#E90638", "#07B423", "#306A8A", "#678225", "#2742FE", "#4C9A75",
#           "#4C36E9", "#7DB022", "#EDAC54", "#EAC439", "#EAC439", "#1A9C45", "#8A51C4", "#496A63", "#FB9543", "#2B49DD",
#           "#13ADA5", "#2DD8C1", "#2E53D7", "#EF9B77", "#06924F", "#AC2C4D", "#82193F", "#0140D3"]

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


def apply(obj, parameters=None):
    if parameters is None:
        parameters = {}

    image_format = "png"
    if "format" in parameters:
        image_format = parameters["format"]

    filename = tempfile.NamedTemporaryFile(suffix='.gv').name

    g = Digraph("", filename=filename, engine='dot',
                graph_attr={'bgcolor': 'transparent'})
    if "ratio" in parameters:
        ratio = parameters["ratio"]
        g.attr(ratio=ratio)
    all_objs = {}
    trans_names = {}

    pl_count = 1
    tr_count = 1
    arc_count = 1

    # color = COLORS[index % len(COLORS)]
    color = "#05B202"
    color_mapping = dict()
    object_types = obj.object_types
    for index, ot in enumerate(object_types):
        color_mapping[ot] = COLORS[index % len(COLORS)]

    for pl in obj.places:
        # this_uuid = str(uuid.uuid4())
        this_uuid = "p%d" % (pl_count)
        # pl_str = this_uuid
        pl_label = ''.join(w[0].upper() for w in pl.name.split())
        pl_count += 1
        color = color_mapping[pl.object_type]
        if pl.initial == True:
            g.node(pl.name, pl_label, shape="circle", style="filled", fillcolor=color, color=color,
                   fontsize="13.0", labelfontsize="13.0")
        elif pl.final == True:
            g.node(pl.name, pl_label, shape="circle", style="filled", color=color, fillcolor=color,
                   fontsize="13.0", labelfontsize="13.0")
        else:
            g.node(pl.name, pl_label, shape="circle", color=color,
                   fontsize="13.0", labelfontsize="13.0")
        all_objs[pl] = pl.name

    for tr in obj.transitions:
        # this_uuid = str(uuid.uuid4())
        this_uuid = "t%d" % (tr_count)
        tr_count += 1
        if tr.silent == True:
            # g.node(this_uuid, this_uuid, fontcolor="#FFFFFF", shape="box",
            #       fillcolor="#000000", style="filled", xlabel="Test", labelfontsize="18.0")
            g.node(tr.name, this_uuid, fontcolor="#FFFFFF", shape="box",
                   fillcolor="#000000", style="filled", xlabel="Test", labelfontsize="13.0")
            all_objs[tr] = tr.name  # this_uuid
        elif tr.name not in trans_names:
            # g.node(this_uuid, "%s \n (%s)" % (tr.name, this_uuid), shape="box", fontsize="36.0",
            #       labelfontsize="36.0")
            g.node(tr.name, tr.name, shape="box", fontsize="13.0",
                   labelfontsize="13.0")
            trans_names[tr.name] = tr.name  # this_uuid
            all_objs[tr] = tr.name  # this_uuid
        else:
            all_objs[tr] = trans_names[tr.name]

    for arc in obj.arcs:
        # this_uuid = str(uuid.uuid4())
        this_uuid = "a%d" % (arc_count)
        arc_count += 1

        source_node = arc.source
        target_node = arc.target

        if type(source_node) == ObjectCentricPetriNet.Place:
            color = color_mapping[source_node.object_type]
        if type(target_node) == ObjectCentricPetriNet.Place:
            color = color_mapping[target_node.object_type]

        if arc.variable == True:
            if source_node in all_objs and target_node in all_objs:
                g.edge(all_objs[source_node], all_objs[target_node],
                       label="", color=color + ":white:" + color, fontsize="13.0")
            else:
                print("Either {} or {} not existing in nodes".format(
                    source_node, target_node))

        else:
            if source_node in all_objs and target_node in all_objs:
                g.edge(all_objs[source_node], all_objs[target_node],
                       label="", color=color, fontsize="13.0")
            else:
                print("Either {} or {} not existing in nodes".format(
                    source_node, target_node))

        all_objs[arc] = this_uuid

    g.attr(overlap='false')
    g.attr(fontsize='11')

    g.format = image_format
    return g
