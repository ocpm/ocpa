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