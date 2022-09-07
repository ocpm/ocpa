
class CorrelatedEventGraph():
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

    def get_sequence(self):
        events = [e for e in self._graph.nodes]
        event_timestamps = [e.time for e in events]
        import operator
        sequence = sorted(events, key=operator.attrgetter('time'))
        sequence = [e.act for e in sequence]
        # event_timestamps = [e.time for e in events]
        # min_index = event_timestamps.index(min(event_timestamps))
        # first_event = events[min_index]
        # return first_event
        return sequence

    def get_event_context_per_object(self, event, ot):
        return set([e for e in self._graph.nodes if (e, event) in self._graph.edges and ot in [self._ovmap[oi].type for oi in event.omap]])

    def get_event_context(self, event):
        # if self.get_first_event() == event:
        #     return None
        # else:
        ots = [self._ovmap[oi].type for oi in event.omap]
        return set([e for e in [e2 for ot in ots for e2 in self.get_event_context_per_object(event, ot)]])

    def get_last_event(self):
        events = [e for e in self._graph.nodes]
        event_timestamps = [e.time for e in events]
        max_index = event_timestamps.index(max(event_timestamps))
        last_event = events[max_index]
        return last_event

    def get_first_event(self):
        events = [e for e in self._graph.nodes]
        event_timestamps = [e.time for e in events]
        min_index = event_timestamps.index(min(event_timestamps))
        first_event = events[min_index]
        return first_event
