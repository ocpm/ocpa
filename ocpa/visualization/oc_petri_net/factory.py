from ocpa.visualization.oc_petri_net.versions import control_flow, annotated_with_opera, new_control_flow, ocpi
from pm4py.visualization.common import gview
from pm4py.visualization.common import save as gsave

CONTROL_FLOW = "control_flow"
NEW_CONTROL_FLOW = "new_control_flow"
ANNOTATED_WITH_OPERA = "annotated_with_opera"
OCPI = "ocpi"

VERSIONS = {
    CONTROL_FLOW: control_flow.apply,
    NEW_CONTROL_FLOW: new_control_flow.apply,
    ANNOTATED_WITH_OPERA: annotated_with_opera.apply,
    OCPI: ocpi.apply
}


def apply(obj, variant=NEW_CONTROL_FLOW, **kwargs):
    return VERSIONS[variant](obj, **kwargs)


def save(gviz, output_file_path):
    """
    Save the diagram

    Parameters
    -----------
    gviz
        GraphViz diagram
    output_file_path
        Path where the GraphViz output should be saved
    """
    gsave.save(gviz, output_file_path)


def view(gviz):
    """
    View the diagram

    Parameters
    -----------
    gviz
        GraphViz diagram
    """
    return gview.view(gviz)
