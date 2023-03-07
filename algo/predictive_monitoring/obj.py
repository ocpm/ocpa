from warnings import warn
import random
import pandas as pd
from sklearn.preprocessing import StandardScaler
from ocpa.objects.log.ocel import OCEL


class Feature_Storage:
    """
    The Feature Storage class stores features extracted for an obejct-centric event log. It stores it in form of feature
    graphs: Each feature graph contains the features for a process execution in form of labeled nodes and graph properties.
    Furthermore, the class provides the possibility to create a training/testing split on the basis of the graphs.
    """

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

        def __init__(self, case_id, graph, ocel: OCEL):
            self._case_id = case_id
            self._nodes = [
                Feature_Storage.Feature_Graph.Node(
                    e_id, ocel.get_value(e_id, "event_objects")
                )
                for e_id in graph.nodes
            ]
            # self._nodes = [Feature_Storage.Feature_Graph.Node(e_id, ocel.log.loc[e_id]["event_objects"]) for e_id in graph.nodes]
            self._node_mapping = {node.event_id: node for node in self._nodes}
            self._objects = {
                (source, target): set(
                    ocel.get_value(source, "event_objects")
                ).intersection(set(ocel.get_value(target, "event_objects")))
                for source, target in graph.edges
            }
            # self._objects = {(source,target):set(ocel.log.loc[source]["event_objects"]).intersection(set(ocel.log.loc[target]["event_objects"])) for source,target in graph.edges}
            self._edges = [
                Feature_Storage.Feature_Graph.Edge(
                    source, target, objects=self._objects[(source, target)]
                )
                for source, target in graph.edges
            ]
            self._edge_mapping = {
                (edge.source, edge.target): edge for edge in self._edges
            }
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
            self._edges = [
                Feature_Storage.Feature_Graph.Edge(
                    source.event_id, target.event_id, objects=[]
                )
                for source, target in edges
            ]

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

    def __init__(
        self,
        event_features: list,
        execution_features: list,
        target_label: str = None,
        ocel: OCEL = None,
        scaler=StandardScaler,
    ):
        self._event_features = event_features
        self._edge_features = []
        self._case_features = execution_features
        self._target_label = target_label
        self._feature_graphs: list[self.Feature_Graph] = []
        self._scaler = scaler
        # self._graph_indices: list[int] = None
        self._train_indices = None
        self._validation_indices = None
        self._test_indices = None

    def _get_event_features(self):
        return self._event_features

    def _set_event_features(self, event_features):
        self._event_features = event_features

    def _get_execution_features(self):
        return self._case_features

    def _set_execution_features(self, execution_features):
        self._case_features = execution_features

    def _get_feature_graphs(self):
        return self._feature_graphs

    def _set_feature_graphs(self, feature_graphs):
        self._feature_graphs = feature_graphs

    def add_feature_graph(self, feature_graph):
        self.feature_graphs += [feature_graph]

    def _get_scaler(self):
        return self._scaler

    def _set_scaler(self, scaler):
        self._scaler = scaler

    def _get_train_indices(self) -> list[int]:
        return self._train_indices

    def _set_train_indices(self, new_train_indices):
        self._train_indices = new_train_indices

    def _get_validation_indices(self) -> list[int]:
        return self._validation_indices

    def _set_validation_indices(self, validation_indices):
        self._validation_indices = validation_indices

    def _get_test_indices(self) -> list[int]:
        return self._test_indices

    def _set_test_indices(self, test_indices):
        self._test_indices = test_indices

    def _get_target_label(self):
        return self._target_label

    def _set_target_label(self, target_label):
        self.__report_target_label_consistency(target_label)
        self._target_label = target_label

    event_features = property(_get_event_features, _set_event_features)
    execution_features = property(_get_execution_features, _set_execution_features)
    feature_graphs = property(_get_feature_graphs, _set_feature_graphs)
    scaler = property(_get_scaler, _set_scaler)
    train_indices = property(_get_train_indices, _set_train_indices)
    validation_indices = property(_get_validation_indices, _set_validation_indices)
    test_indices = property(_get_test_indices, _set_test_indices)
    target_label = property(_get_target_label, _set_target_label)

    def _event_id_table(self, feature_graphs: list[Feature_Graph]) -> pd.DataFrame:
        features = self.event_features
        df = pd.DataFrame(columns=["event_id"] + [features])
        dict_list = []
        for g in feature_graphs:
            for node in g.nodes:
                dict_list.append({**{"event_id": node.event_id}, **node.attributes})
                # print(node.attributes)
        df = pd.DataFrame(dict_list)
        return df

    def _create_mapper(self, table: pd.DataFrame) -> dict:
        arr = table.to_numpy()
        column_mapping = {k: v for v, k in enumerate(list(table.columns.values))}
        mapper = dict()
        for row in arr:
            e_id = row[column_mapping["event_id"]]
            mapper[e_id] = {
                k: row[column_mapping[k]]
                for k in column_mapping.keys()
                if k != "event_id"
            }
        return mapper

    def __report_target_label_consistency(self, target_label: tuple) -> None:
        """
        Method that hides dynamic (but ugly) warning, which is issued when 'target_label' passed to
        method 'extract_normalized_train_test_split' is unequal to 'self.target_label'.

        This method probably indicates a design flaw that is consciously ignored.
        """
        if self.target_label:
            if self.target_label != target_label:
                warn(
                    message=f"Passed parameter '{f'{target_label=}'.partition('=')[0]}' unequal to {self.__class__.__name__}.{f'{self.target_label=}'.partition('=')[0].split('.')[1]}. Expected '{self.target_label}', while '{target_label}' was given. Please pass the same value to {self.__class__} '{self.__init__.__name__}' as '{self.extract_normalized_train_test_split.__qualname__}'.",
                    category=RuntimeWarning,
                )

    def __map_graph_values(self, mapper, graphs: Feature_Graph) -> None:
        """
        Impure private method that sets graph features to scaled values.

        It changes the node attribute values of the graphs passed
        Therefore, its impure/in_place.
        """
        for g in graphs:
            for node in g.nodes:
                for att in node.attributes.keys():
                    node.attributes[att] = mapper[node.event_id][att]

    def __normalize_feature_graphs(
        self, graphs: list[Feature_Graph], initialized_scaler, train: bool
    ) -> None:
        """
        Impure private method that, given a list of graphs and an initialized scaler object,
        normalizes the given graphs in an impure fashion (in_place).

        :param train: Mandatory. To prevent data leakage by using information from train set to
         normalize the validation or test set.
        :type train: bool

        Therefore, please do not use this from outside the class.
        """
        table = self._event_id_table(graphs)
        if train:
            table[self.event_features] = initialized_scaler.fit_transform(
                X=table[self.event_features]
            )
        else:
            table[self.event_features] = initialized_scaler.transform(
                X=table[self.event_features]
            )
        # Update graphs' feature values
        mapper = self._create_mapper(table)  # for efficiency
        self.__map_graph_values(mapper, graphs)

    def extract_normalized_train_test_split(
        self,
        test_size: float,
        validation_size: float = 0,
        target_label: tuple = None,
        state: int = 42,
    ) -> None:
        """
        Splits and normalizes the feature storage. Each split is normalized according to it's member, i.e., the testing
        set is not normalized with information of the training set. The splitting information is stored in form of
        index lists as properties of the feature storage object.
        :param test_size: Between 0 and 1, indicates the share of the data that should go to the test set.
        :type test_size: float

        :param validation_size: Between 0 and 1, indicates the share of the data (percentage points) that should go
        to the validation set. It takes this from the training set size.
        :type validation_size: float

        :param target_label: The label of the target variable, the one that will be predicted by a model. If passed,
        the target variable will be excluded from normalization.
        :type state: str

        :param state: Random state of the splitting. Can be used to reproduce splits.
        :type state: int
        """
        # Set train/val/test indices
        train_size = 1 - validation_size - test_size
        if validation_size >= train_size:
            raise ValueError(
                f"validation_size ({validation_size}) must be smaller than train_size (= 1-test_size = {train_size})"
            )
        graph_indices = list(range(0, len(self.feature_graphs)))
        random.Random(state).shuffle(graph_indices)
        ################################################
        ##       VISUALIZATION OF THE SPLITTING       ##
        ##  @@@@@@@@@@@@@@@@@@ $$$$$$$$ &&&&&&&&&&&&  ##
        ##        train          val        test      ##
        ##         50%           20%        30%       ##
        ##                    |        |              ##
        ##                    v        v              ##
        ##             train_spl_idx  val_spl_idx     ##
        ################################################
        train_split_idx = int(train_size * len(graph_indices))
        val_split_idx = int((train_size + validation_size) * len(graph_indices))
        self._set_train_indices(graph_indices[:train_split_idx])
        self._set_validation_indices(graph_indices[train_split_idx:val_split_idx])
        self._set_test_indices(graph_indices[val_split_idx:])

        # Get train/val/test graphs
        train_graphs, val_graphs, test_graphs = (
            [self.feature_graphs[i] for i in self._train_indices],
            [self.feature_graphs[i] for i in self._validation_indices],
            [self.feature_graphs[i] for i in self._test_indices],
        )

        # Prepare for normalization (ensure y is excluded)
        scaler = self.scaler()
        if target_label:
            self._set_target_label(target_label)
        if self.target_label:
            self.event_features.remove(
                self.target_label
            )  # remove y-label s.t. it'll be excluded from normalization

        # Normalize training, validation, and testing set
        self.__normalize_feature_graphs(train_graphs, scaler, train=True)
        if validation_size:
            self.__normalize_feature_graphs(val_graphs, scaler, train=False)
        self.__normalize_feature_graphs(test_graphs, scaler, train=False)

        # Store normalization information for reproducibility
        self._set_scaler(scaler)
