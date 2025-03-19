class OCEvent:
    def __init__(self):
        self.event_id = None  # integer
        self.event_name = None
        self.objects = None  # list of object_ids
        self.datetime = None  # datetime

    def __str__(self):
        return f"Event {self.event_id} {self.event_name} at {self.datetime.strftime('%d-%m-%Y %H:%M')} with objects: {self.objects}"


class ProcessExecutionGraph:
    def __init__(self):
        # the obj_instance_based_dict is a dict that has the obj instances as keys and all the events that belong
        # to those obj instance as a list as the value
        # This allows quick creation of dependencies
        self.obj_instance_based_dict = {}
        self.connections = set()
        self.number_of_events = 0

    def add_event(self, event):
        if not isinstance(event, OCEvent):
            raise Exception("Event hat to be OCEvent in ProcessExecutionGraph add_event")

        for obj_instance in event.objects:
            if obj_instance not in self.obj_instance_based_dict.keys():
                self.obj_instance_based_dict[obj_instance] = []

            self.obj_instance_based_dict[obj_instance].append(event)

        self.number_of_events += 1

        # XXX OPTIMIZATION: Instead of sorting in the end directly insert into sorted list with binary insert

    def update_dependencies(self):
        for event_list in self.obj_instance_based_dict.values():
            # sort for each object instance
            event_list.sort(key=lambda ev: ev.datetime)

    def show(self):
        for obj_instance, ev_list in self.obj_instance_based_dict.items():
            print(f"{obj_instance}: ", end='')
            for event in ev_list:
                print(f"-> ({event.event_id} @ {event.datetime.strftime('%d-%m-%Y %H:%M')}) ", end='')
            print('')

    def is_empty(self):
        return self.number_of_events <= 0

    def drop_next_event_leaf_to_head(self):
        for ev_list in self.obj_instance_based_dict.values():
            if not ev_list:
                continue
            first_ev = ev_list[0]
            # check whether first event only appears as first event
            first_ev_is_only_first = True
            for event_list in self.obj_instance_based_dict.values():
                if first_ev in event_list[1:]:
                    first_ev_is_only_first = False
                    break
            if first_ev_is_only_first:
                # a leaf was found - that leaf will be dropped
                for event_list in self.obj_instance_based_dict.values():
                    if first_ev in event_list:
                        event_list.remove(first_ev)
                self.number_of_events -= 1
                return first_ev
