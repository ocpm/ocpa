class EventGraph():
    def __init__(self, name=None, graph=None, otmap=None, ovmap=None):
        self._name = name
        self._graph = graph
        self._otmap = otmap
        self._ovmap = ovmap

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self._name = name

    @property
    def graph(self):
        return self._graph

    @graph.setter
    def graph(self, graph):
        self._graph = graph

    @property
    def otmap(self):
        return self._otmap

    @otmap.setter
    def otmap(self, otmap):
        self._otmap = otmap

    @property
    def ovmap(self):
        return self._ovmap

    @ovmap.setter
    def ovmap(self, ovmap):
        self._ovmap = ovmap
