class Feature_Storage:
    class Feature_Graph:
        class Node:
            def __init__(self, event_id, objects):
                self._event = event_id
                self._attributes = {}
                self._objects = objects

            def add_attribute(self, key, value):
                self._attributes[key] = value

            def _get_attributes(self):
                return self._attributes

            def _get_objects(self):
                return self._objects

            def _get_event_id(self):
                return self._event
            event_id = property(_get_event_id)
            attributes = property(_get_attributes)
            objects = property(_get_objects)

        class Edge:
            def __init__(self, source, target, objects):
                self._source = source
                self._target = target
                self._objects = objects
                self._attributes = {}

            def add_attribute(self, key, value):
                self._attributes[key] = value

            def _get_source(self):
                return self._source

            def _get_target(self):
                return self._target

            def _get_objects(self):
                return self._objects

            def _get_attributes(self):
                return self._attributes

            attributes = property(_get_attributes)
            source = property(_get_source)
            target = property(_get_target)
            objects = property(_get_objects)

        def __init__(self, case_id, graph, ocel):
            self._case_id = case_id
            self._nodes = [Feature_Storage.Feature_Graph.Node(e_id, ocel.get_value(e_id,"event_objects")) for e_id in
                           graph.nodes]
            #self._nodes = [Feature_Storage.Feature_Graph.Node(e_id, ocel.log.loc[e_id]["event_objects"]) for e_id in graph.nodes]
            self._node_mapping = {node.event_id:node for node in self._nodes}
            self._objects = {(source, target): set(ocel.get_value(source,"event_objects")).intersection(
                set(ocel.get_value(target,"event_objects"))) for source, target in graph.edges}
            #self._objects = {(source,target):set(ocel.log.loc[source]["event_objects"]).intersection(set(ocel.log.loc[target]["event_objects"])) for source,target in graph.edges}
            self._edges = [Feature_Storage.Feature_Graph.Edge(source,target, objects = self._objects[(source,target)])for source,target in graph.edges]
            self._edge_mapping = {(edge.source,edge.target): edge for edge in self._edges}
            self._attributes = {}

        def _get_nodes(self):
            return self._nodes

        def _get_edges(self):
            return self._edges

        def _get_objects(self):
            return self._objects

        def _get_attributes(self):
            return self._attributes

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

    def __init__(self, event_features, execution_features, ocel):
        self._event_features = event_features
        self._edge_features = []
        self._case_features = execution_features
        self._feature_graphs = []

    def _get_event_features(self):
        return self._event_features

    def _set_event_features(self, event_features):
        self._event_features = event_features

    def _get_feature_graphs(self):
        return self._feature_graphs

    def _set_feature_graphs(self, feature_graphs):
        self._feature_graphs = feature_graphs

    def add_feature_graph(self, feature_graph):
        self.feature_graphs += [feature_graph]

    def _get_execution_features(self):
        return self._case_features

    def _set_execution_features(self, execution_features):
        self._case_features = execution_features

    event_features = property(_get_event_features, _set_event_features)
    execution_features = property(_get_execution_features, _set_execution_features)
    feature_graphs = property(_get_feature_graphs, _set_feature_graphs)
