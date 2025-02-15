import uuid
import tempfile
from graphviz import Digraph
from ocpa.objects.oc_petri_net.obj import ObjectCentricPetriNet

COLORS = [
    '#7f66ff',
    '#ff3399',
    '#f58b55',
    '#f25e65',
    '#261926',  # too dark
    '#ddb14d',
    '#5387d5',
    '#1c3474',  # too dark
    '#a37554',
    '#8bc34a',
    '#cddc39',
    '#ffeb3b',
    '#ffc107',
    '#ff9800',
    '#ff5722',
    '#795548',  # borderline
    '#9e9e9e',  # gray
    '#607d8b',  # borderline
    '#9affff',
    '#000000'
]


def is_color_too_dark(hex_color: str, luminance_threshold: float = 0.2) -> bool:
    """
    Determines if a hex color is too dark based on its relative luminance.

    Args:
        hex_color (str): The hex color code string (e.g., "#1c3474").
        luminance_threshold (float): The luminance threshold below which the color is considered too dark.

    Returns:
        bool: True if the color is too dark, False otherwise.
    """
    # Remove the hash (#) if present
    hex_color = hex_color.lstrip('#')

    # Convert the hex color to RGB components (0-255 range)
    r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)

    # Normalize RGB values to 0-1 range
    r /= 255.0
    g /= 255.0
    b /= 255.0

    # Calculate the relative luminance based on the sRGB formula
    def adjust(color_component):
        return color_component / 12.92 if color_component <= 0.03928 else ((color_component + 0.055) / 1.055) ** 2.4

    r, g, b = adjust(r), adjust(g), adjust(b)
    luminance = 0.2126 * r + 0.7152 * g + 0.0722 * b

    # Return True if the luminance is below the threshold
    return luminance < luminance_threshold


def apply(ocpn: ObjectCentricPetriNet, parameters=None):
    if parameters is None:
        parameters = {}

    image_format = parameters.get('format') or "png"
    background_color = parameters.get('bgcolor') or "transparent"

    filename = tempfile.NamedTemporaryFile(suffix='.gv').name

    g = Digraph("", filename=filename, engine='dot', graph_attr={'bgcolor': background_color})

    if ratio := parameters.get('ratio'):
        g.attr(ratio=ratio)

    all_objs = {}
    trans_names = {}

    pl_count = 1
    tr_count = 1

    # color = COLORS[index % len(COLORS)]
    color = "#05B202"
    color_mapping = dict()
    object_types = ocpn.object_types
    for index, ot in enumerate(object_types):
        color_mapping[ot] = COLORS[index % len(COLORS)]

    for pl in ocpn.places:
        this_uuid = str(uuid.uuid4())
        pl_label = pl.object_type
        pl_count += 1
        color = color_mapping[pl.object_type]
        label_color = "white" if is_color_too_dark(color) else "black"
        if pl.initial == True or pl.final == True:
            g.node(
                this_uuid, pl_label, shape="circle", style="filled", fillcolor=color, color=color,
                fontcolor=label_color, fontsize="13.0", labelfontsize="13.0", width="0.5",
                height="0.5"
            )
        else:
            g.node(
                this_uuid, "", shape="circle", color=color,
                fontsize="13.0", labelfontsize="13.0", width="0.5", height="0.5"
            )
        all_objs[pl] = this_uuid

    for tr in ocpn.transitions:
        this_uuid = str(uuid.uuid4())
        tr_count += 1
        if tr.silent == True:
            g.node(this_uuid, "", fontcolor="#FFFFFF", shape="box",
                   fillcolor="#000000", style="filled", width="0.1", height="0.1")  # Even smaller size
            all_objs[tr] = this_uuid  # this_uuid
        elif tr.label not in trans_names:
            g.node(this_uuid, tr.label, shape="box", fontsize="13.0",
                   labelfontsize="13.0", width="0.7", height="0.7")  # Larger size
            trans_names[tr.label] = tr.label  # this_uuid
            all_objs[tr] = this_uuid
        else:
            all_objs[tr] = this_uuid

    for arc in ocpn.arcs:
        this_uuid = str(uuid.uuid4())

        if type(arc.source) == ObjectCentricPetriNet.Place:
            color = color_mapping[arc.source.object_type]
        if type(arc.target) == ObjectCentricPetriNet.Place:
            color = color_mapping[arc.target.object_type]

        if arc.variable == True:
            g.edge(all_objs[arc.source], all_objs[arc.target], label="",
                   color=color + ":white:" + color, fontsize="13.0")
        else:
            g.edge(all_objs[arc.source], all_objs[arc.target],
                   label="", color=color, fontsize="13.0")

        all_objs[arc] = this_uuid

    g.attr(overlap='false')
    g.attr(fontsize='11')

    g.format = image_format
    return g
