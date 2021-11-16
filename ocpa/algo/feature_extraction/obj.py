class Feature_Storage:
    class Feature_Graph:
        class Node:
            def __init__(self, event):
                self._event = None
                self._attributes = {}
        class Edge:
            def __init__(self, source, target, objects):
                self._source = source
                self._target = target
                self._objects = objects
                self._attributes = {}

        def __init__(self, case_id):
            self._case_id = case_id
            self._nodes = []
            self._edges = []
            self._attributes = {}

    def __init__(self):
        self._event_features = []
        self._case_features = []
        self._feature_graphs = []

