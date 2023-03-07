class Feature_Graph:
    def __init__(self, case_id, graph, ocel):
        self._case_id = case_id
        self._nodes = [Feature_Storage.Feature_Graph.Node(e_id, ocel.get_value(e_id, "event_objects")) for e_id in
                       graph.nodes]
        #self._nodes = [Feature_Storage.Feature_Graph.Node(e_id, ocel.log.loc[e_id]["event_objects"]) for e_id in graph.nodes]
        self._node_mapping = {node.event_id: node for node in self._nodes}
        self._objects = {(source, target): set(ocel.get_value(source, "event_objects")).intersection(
            set(ocel.get_value(target, "event_objects"))) for source, target in graph.edges}
        #self._objects = {(source,target):set(ocel.log.loc[source]["event_objects"]).intersection(set(ocel.log.loc[target]["event_objects"])) for source,target in graph.edges}
        self._edges = [Feature_Storage.Feature_Graph.Edge(
            source, target, objects=self._objects[(source, target)])for source, target in graph.edges]
        self._edge_mapping = {
            (edge.source, edge.target): edge for edge in self._edges}
        self._attributes = {}

    def _get_nodes(self):
        return self._nodes

    def _get_edges(self):
        return self._edges

    def _get_objects(self):
        return self._objects

    def _get_attributes(self):
        return self._attributes

    def replace_edges(self, edges):
        self._edges = [Feature_Storage.Feature_Graph.Edge(
            source.event_id, target.event_id, objects=[]) for source, target in edges]

    def get_node_from_event_id(self, event_id):
        return self._node_mapping[event_id]

    def get_edge_from_event_ids(self, source, target):
        return self._edge_mapping[(source, target)]

    def add_attribute(self, key, value):
        self._attributes[key] = value

    attributes = property(_get_attributes)
    nodes = property(_get_nodes)
    edges = property(_get_edges)
    objects = property(_get_objects)