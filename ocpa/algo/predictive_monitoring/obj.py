import pandas as pd
from sklearn.preprocessing import StandardScaler
import random


class Feature_Storage:
    '''
    The Feature Storage class stores features extracted for an obejct-centric event log. It stores it in form of feature
    graphs: Each feature graph contains the features for a process execution in form of labeled nodes and graph properties.
    Furthermore, the class provides the possibility to create a training/testing split on the basis of the graphs.
    '''

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

    def __init__(self, event_features, execution_features, ocel):
        self._event_features = event_features
        self._edge_features = []
        self._case_features = execution_features
        self._feature_graphs = []
        self._scaler = None
        self._training_indices = None
        self._test_indices = None

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

    def _get_training_indices(self):
        return self._training_indices

    def _get_test_indices(self):
        return self._test_indices

    def _get_scaler(self):
        return self._scaler

    event_features = property(_get_event_features, _set_event_features)
    execution_features = property(
        _get_execution_features, _set_execution_features)
    feature_graphs = property(_get_feature_graphs, _set_feature_graphs)
    training_indices = property(_get_training_indices)
    test_indices = property(_get_test_indices)
    scaler = property(_get_scaler)

    def _event_id_table(self, feature_graphs):
        features = self.event_features
        df = pd.DataFrame(columns=["event_id"] + [features])
        dict_list = []
        for g in feature_graphs:
            for node in g.nodes:
                dict_list.append(
                    {**{"event_id": node.event_id}, **node.attributes})
                # print(node.attributes)
        df = pd.DataFrame(dict_list)
        return df

    def _create_mapper(self, table):
        arr = table.to_numpy()
        column_mapping = {k: v for v, k in enumerate(
            list(table.columns.values))}
        mapper = dict()
        for row in arr:
            e_id = row[column_mapping["event_id"]]
            mapper[e_id] = {k: row[column_mapping[k]]
                            for k in column_mapping.keys() if k != "event_id"}
        return mapper

    def extract_normalized_train_test_split(self, test_size, state=1):
        '''
        Splits and normalizes the feature storage. Each split is normalized according to it's member, i.e., the testing
        set is not normalized with information of the training set. The splitting information is stored in form of
        index lists as properties of the feature storage object.
        :param test_size: Between 0 and 1, indicates the share of the data that should go to the test set.
        :type test_size: float

        :param state: random state of the splitting. Can be used to reproduce splits
        :type state: int


        '''

        graphs_indices = list(range(0, len(self.feature_graphs)))
        random.Random(state).shuffle(graphs_indices)
        split_index = int((1-test_size)*len(graphs_indices))
        # print(split_index)
        self._training_indices = graphs_indices[:split_index]
        self._test_indices = graphs_indices[split_index:]
        train_graphs, test_graphs = [self.feature_graphs[i] for i in self._training_indices], [
            self.feature_graphs[i] for i in self._test_indices]
        # Normalize
        features = self.event_features
        train_table = self._event_id_table(train_graphs)
        test_table = self._event_id_table(test_graphs)
        scaler = StandardScaler()
        train_table[self.event_features] = scaler.fit_transform(
            train_table[self.event_features])
        test_table[self.event_features] = scaler.transform(
            test_table[self.event_features])
        self._scaler = scaler
        # update features features
        # for efficiency
        train_mapper = self._create_mapper(train_table)
        test_mapper = self._create_mapper(test_table)
        # change original values!
        for g in [self.feature_graphs[i] for i in self.training_indices]:
            for node in g.nodes:
                for att in node.attributes.keys():
                    node.attributes[att] = train_mapper[node.event_id][att]
        for g in [self.feature_graphs[i] for i in self.test_indices]:
            for node in g.nodes:
                for att in node.attributes.keys():
                    node.attributes[att] = test_mapper[node.event_id][att]
