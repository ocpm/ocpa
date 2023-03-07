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