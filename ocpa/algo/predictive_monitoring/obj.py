import random
from warnings import warn

import pandas as pd
<<<<<<< HEAD
from sklearn.preprocessing import StandardScaler

from ocpa.objects.log.ocel import OCEL
=======
# from sklearn.preprocessing import StandardScaler
from ocpa.util.util import StandardScaler
import random
>>>>>>> upstream/main

class Feature_Storage:
    """
    The Feature Storage class stores features extracted for an object-centric event log. It stores it in form of feature
    graphs: Each feature graph contains the features for a process execution in form of labeled nodes and graph properties.
    Furthermore, the class provides the possibility to create a training/testing split on the basis of the graphs.
    """

    class Feature_Graph:
        class Node:
            def __init__(self, event_id, objects, pexec_id):
                """Initializes a Node object"""
                self._event = event_id
                self._attributes = {}
                self._objects = objects
                self._pexec_id = pexec_id

            def add_attribute(self, key, value) -> None:
                self._attributes[key] = value

            def _get_attributes(self):
                return self._attributes

            def _get_objects(self):
                return self._objects

            def _get_event_id(self):
                return self._event

            def _get_pexec_id(self):
                return self._pexec_id

            event_id = property(_get_event_id)
            attributes = property(_get_attributes)
            objects = property(_get_objects)
            pexec_id = property(_get_pexec_id)

        class Edge:
            def __init__(self, source, target, objects):
                """Initializes an Edge object"""
                self._source = source
                self._target = target
                self._objects = objects
                self._attributes = {}

            def add_attribute(self, key, value) -> None:
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

        def __init__(self, pexec_id, graph, ocel):
            self._pexec_id = pexec_id
            self._nodes = [
                Feature_Storage.Feature_Graph.Node(
                    e_id, ocel.get_value(e_id, "event_objects"), pexec_id
                )
                for e_id in graph.nodes
            ]
            self._node_mapping = {node.event_id: node for node in self._nodes}
            self._objects = {
                (source, target): set(
                    ocel.get_value(source, "event_objects")
                ).intersection(set(ocel.get_value(target, "event_objects")))
                for source, target in graph.edges
            }
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

        def _get_nodes(self) -> list[Node]:
            return self._nodes

        def _get_pexec_id(self):
            return self._pexec_id

        def _get_edges(self) -> list[Edge]:
            return self._edges

        def _get_objects(self) -> dict[tuple, set]:
            return self._objects

        def _get_attributes(self) -> dict:
            return self._attributes

        def _get_size(self) -> int:
            return len(self._get_nodes())

        def replace_edges(self, edges) -> None:
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

        def add_attribute(self, key, value) -> None:
            self._attributes[key] = value

        nodes = property(_get_nodes)  # : list[Node]
        edges = property(_get_edges)  # : list[Edge]
        objects = property(_get_objects)  # : dict[tuple, set]
        attributes = property(_get_attributes)  # : dict
        size = property(_get_size)  # : int
        pexec_id = property(_get_pexec_id)  # : int

    def __init__(
        self,
        event_features: list,
        execution_features: list,
        ocel: OCEL = None,
    ):
        """Initializes a Feature_Storage object"""
        self._event_features = event_features
        self._edge_features = []
        self._case_features = execution_features
        self._feature_graphs: list[self.Feature_Graph] = []
        self._scaler = None
        self._scaling_exempt_features: list[tuple] = []
        self._train_indices: list[int] = []
        self._validation_indices: list[int] = []
        self._test_indices: list[int] = []

    def _get_event_features(self):
        return self._event_features

    def _set_event_features(self, event_features) -> None:
        self._event_features = event_features

    def _get_execution_features(self):
        return self._case_features

    def _set_execution_features(self, execution_features) -> None:
        self._case_features = execution_features

    def _get_feature_graphs(self) -> list[Feature_Graph]:
        return self._feature_graphs

    def _set_feature_graphs(self, feature_graphs: list[Feature_Graph]) -> None:
        self._feature_graphs = feature_graphs

    def add_feature_graph(self, feature_graph: Feature_Graph) -> None:
        self.feature_graphs += [feature_graph]

    def _get_scaler(self):
        return self._scaler

    def _set_scaler(self, scaler) -> None:
        self._scaler = scaler

    def _get_train_indices(self) -> list[int]:
        return self._train_indices

    def _set_train_indices(self, new_train_indices: list[int]) -> None:
        self._train_indices = new_train_indices

    def _get_validation_indices(self) -> list[int]:
        return self._validation_indices

    def _set_validation_indices(self, validation_indices):
        self._validation_indices = validation_indices

    def _get_test_indices(self) -> list[int]:
        return self._test_indices

    def _set_test_indices(self, test_indices) -> None:
        self._test_indices = test_indices

    def _get_scaling_exempt_features(self) -> list[tuple]:
        return self._scaling_exempt_features

    def _set_scaling_exempt_features(
        self, scaling_exempt_features: list[tuple]
    ) -> None:
        self._scaling_exempt_features = scaling_exempt_features

    event_features = property(_get_event_features, _set_event_features)
    execution_features = property(_get_execution_features, _set_execution_features)
    feature_graphs = property(
        _get_feature_graphs, _set_feature_graphs
    )  # : list[Feature_Graph]
    scaler = property(_get_scaler, _set_scaler)
    train_indices = property(_get_train_indices, _set_train_indices)  # : list[int]
    validation_indices = property(
        _get_validation_indices, _set_validation_indices
    )  # : list[int]
    test_indices = property(_get_test_indices, _set_test_indices)  # : list[int]
    scaling_exempt_features = property(
        _get_scaling_exempt_features, _set_scaling_exempt_features
    )  # : list[tuple]

    def _event_id_table(self, feature_graphs: list[Feature_Graph]) -> pd.DataFrame:
        """
        Create an event ID table from a list of feature graphs.

        Args:
            feature_graphs (list[Feature_Graph]): A list of Feature_Graph objects containing event information.

        Returns:
            pd.DataFrame: A DataFrame representing the event ID table.

        Example:
            The DataFrame will have columns representing event information, such as event_id and attributes.

            event_id | attribute_1 | attribute_2 | ... | attribute_n
            -------------------------------------------------------
            1        | value_1_1   | value_1_2   | ... | value_1_n
            2        | value_2_1   | value_2_2   | ... | value_2_n
            ...      | ...         | ...         | ... | ...
            m        | value_m_1   | value_m_2   | ... | value_m_n
        """
        dict_list = []
        for fg in feature_graphs:
            for node in fg.nodes:
                dict_list.append({**{"event_id": node.event_id}, **node.attributes})
        fg_table = pd.DataFrame(dict_list)
        return fg_table

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

    def __map_graph_values(self, mapper, graphs: list[Feature_Graph]) -> None:
        """
        Private method (impure) that sets graph features to scaled values.

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
        Private method (impure) that, given a list of graphs and an initialized scaler object,
        normalizes the given graphs in an impure fashion (inplace).

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
        # Update graphs' feature values from the normalized `table`
        mapper = self._create_mapper(table)  # for efficiency
        self.__map_graph_values(mapper, graphs)

    def denormalize(
        self, normalized_data: dict[str, list[float]] or pd.DataFrame
    ) -> dict[str, list[float]]:
        """
        Returns denormalized data (in same format as input), when given a dictionary with
        variable names as keys and lists of normalized floats as values.

        :param normalized_data: Between 0 and 1, indicates the share of the data that should go to the test set.
        :type normalized_data: dict[str, list[float]] or pd.DataFrame
        """
        # # For easy consistency checks:
        # if type(normalized_data) == dict and all_keys_in_feature_storage:
        #     normalized_data = pd.DataFrame(normalized_data)

        # Consistency checks (both for if `normalized_data` is dict and pd.DataFrame)
        if type(normalized_data) == dict:
            all_values_have_equal_length = (
                len(set([len(v) for v in normalized_data.values()])) == 1
            )
            assert (
                all_values_have_equal_length
            ), f"All values in `normalized_data` should be of equal length"
            len_normalized_data = len(list(normalized_data.values())[0])
        if type(normalized_data) == pd.DataFrame:
            len_normalized_data = len(normalized_data)
        num_event_features = len(self.event_features)

        # all_keys_in_feature_storage = all(
        #     [var_name in self.event_features for var_name in normalized_data.keys()]
        # )
        # assert (
        #     all_keys_in_feature_storage
        # ), f"All keys in `normalized_data` should exist as event features in Feature_Storage"

        keys_not_in_event_features = set(normalized_data.keys()) - set(
            self.event_features
        )
        warn(
            f"Could not find keys '{keys_not_in_event_features}' as event features in Feature_Storage. They will be excluded from denormalization."
        )
        valid_keys = set(normalized_data.keys()) & set(self.event_features)

        idxs_of_valid_keys_in_event_feats = {
            self.event_features.index(key) for key in valid_keys
        }
        empty_dict = {
            k: v
            for (k, v) in zip(
                range(num_event_features),
                [[0] * len_normalized_data] * num_event_features,
            )
        }

        for key_idx, key in zip(idxs_of_valid_keys_in_event_feats, valid_keys):
            for k, _ in empty_dict.items():
                if key_idx == k:
                    empty_dict.update({key_idx: normalized_data[key]})
            empty_dict[key] = empty_dict.pop(key_idx)
        self.empty_dict = empty_dict
        prepared_normalized_data = pd.DataFrame(empty_dict)
        self.prepared_normalized_data = prepared_normalized_data
        col_name_map = {k: v for k, v in enumerate(self.event_features)}
        self.col_name_map = col_name_map
        prepared_normalized_data.rename(columns=col_name_map, inplace=True)
        # create dict with length that `X` requires (=len(self.event_features)+1)
        # fill it with keys as index numbers, from 0 to n
        # fill it with values as lists containing 0, and length equal to len(normalized_data.values()[0])

        # look up which column belongs to which key,
        # for column in `X` expected by scaler.inverse_transform()
        # and replace these keys with the values that were given at that key-column-index in normalized_data

        return self.scaler.inverse_transform(prepared_normalized_data)

    def _set_train_test_split(
        self,
        test_size: float,
        validation_size: float = 0,
        state: int = None,
    ):
        """
        Set up the train-validation-test split for the feature graphs.

        Parameters:
            test_size (float): The proportion of the data to include in the test set.
            validation_size (float, optional): The proportion of the data to include in the validation set.
                                               Default is 0, indicating no validation set.
            state (int, optional): Random seed for shuffling the data. Default is None.

        Raises:
            ValueError: If validation_size is greater than or equal to the train_size.

        Note:
            The train_size is calculated as 1 - validation_size - test_size.

        ################################################
        ##      VISUALIZATION OF THE SPLITTING :)     ##
        ##        train          val        test      ##
        ##         50%           20%        30%       ##
        ##  @@@@@@@@@@@@@@@@@@ $$$$$$$$ &&&&&&&&&&&&  ##
        ##                    |        |              ##
        ##                    v        v              ##
        ##             train_spl_idx  val_spl_idx     ##
        ################################################
        """
        # Derive train set size
        train_size = 1 - validation_size - test_size
        if validation_size >= train_size:
            raise ValueError(
                f"validation_size ({validation_size}) must be smaller than train_size (= 1-test_size = {train_size})"
            )
        # Generate a list of indices corresponding to the feature graphs
        graph_indices = list(range(0, len(self.feature_graphs)))
        # Shuffle the graph indices based on the provided random seed (state)
        random.Random(state).shuffle(graph_indices)
        # Calculate the indices to split the data into train, validation, and test sets
        train_split_idx = int(train_size * len(graph_indices))
        val_split_idx = int((train_size + validation_size) * len(graph_indices))
        # Set the indices for train, validation, and test sets
        self._set_train_indices(graph_indices[:train_split_idx])
        self._set_validation_indices(graph_indices[train_split_idx:val_split_idx])
        self._set_test_indices(graph_indices[val_split_idx:])

    def _get_train_test_split(
        self,
    ) -> dict[str, list[Feature_Graph]]:
        """
        Get the train-validation-test split of the feature graphs.

        Returns:
            dict[str, list[Feature_Graph]]: A dictionary containing the train, validation, and test sets of feature graphs.

        Note:
            The feature graphs are obtained based on the indices previously set using `_set_train_test_split`.

        Example:
            {
                "train": [Feature_Graph1, Feature_Graph2, ...],
                "valid": [Feature_Graph3, Feature_Graph4, ...],
                "test": [Feature_Graph5, Feature_Graph6, ...],
            }
        """
        return {
            "train": [self.feature_graphs[i] for i in self._train_indices],
            "valid": [self.feature_graphs[i] for i in self._validation_indices],
            "test": [self.feature_graphs[i] for i in self._test_indices],
        }

    def extract_normalized_train_test_split(
        self,
        scaler,
        test_size: float,
        validation_size: float = 0,
        scaling_exempt_features: list[tuple] = [],
        state: int = None,
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

        :param scaler: Scaler from Scikit-learn (uses .fit_transform() and .transform())
        :type Mixin from Scikit-learn: :class:`Some mixin based on: (OneToOneFeatureMixin, TransformerMixin, BaseEstimator)`

        :param scaling_exempt_features: The names of features that will be excluded form normalization. If passed,
        the these variables will be excluded from normalization. A common use case would be the target variable.
        :type state: list[tuple]

        :param state: Random state of the splitting. Can be used to reproduce splits.
        :type state: int
        """
        # Set train/valid/test indices
        self._set_train_test_split(
            test_size=test_size, validation_size=validation_size, state=state
        )

        # Get train/valid/test graphs
        split_graphs_dict = self._get_train_test_split()

        # Prepare for normalization (ensure scaling_exempt_features are excluded)
        if scaling_exempt_features:
            for feature in scaling_exempt_features:
                # remove scaling_exempt_features s.t. they'll be excluded from normalization
                try:
                    self.event_features.remove(feature)
                except:
                    warning_msg = f"{feature} in 'scaling_exempt_features' cannot be found in 'self.event_features'."
                    warn(warning_msg)
            self._set_scaling_exempt_features(scaling_exempt_features)
        scaler = scaler()  # initialize scaler object

        # Normalize training, validation, and testing set
        self.__normalize_feature_graphs(split_graphs_dict["train"], scaler, train=True)
        if validation_size:
            self.__normalize_feature_graphs(
                split_graphs_dict["valid"], scaler, train=False
            )
        self.__normalize_feature_graphs(split_graphs_dict["test"], scaler, train=False)

        # Store normalization information for reproducibility
        # self._set_scaler(scaler)
        self.scaler = scaler
