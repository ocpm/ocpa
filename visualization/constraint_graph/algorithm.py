from ocpa.visualization.constraint_graph.versions import to_cytoscape


TO_CYTOSCAPE = "to_cytoscape"

VERSIONS = {
    TO_CYTOSCAPE: to_cytoscape.apply}


def apply(obj, variant=TO_CYTOSCAPE, **kwargs):
    return VERSIONS[variant](obj, **kwargs)
