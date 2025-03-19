from ocpa.objects.oc_petri_net.obj import ObjectCentricPetriNet
from dataclasses import dataclass, field, fields
from typing import List, FrozenSet, Set, Dict, Tuple, Optional

from collections import Counter
import linecache
import os
import tracemalloc
from ocpa.objects.log.importer.ocel import factory as ocel_import_factory

import math
from datetime import datetime, timedelta, timezone

def set_place_to_final(place: ObjectCentricPetriNet.Place, ocpn: ObjectCentricPetriNet) -> ObjectCentricPetriNet.Place:
    # create new place
    new_place = ObjectCentricPetriNet.Place(place.name, place.object_type, final=True)
    ocpn.places.add(new_place)
    # recreate all arcs
    for arc in place.in_arcs:
        new_arc = ObjectCentricPetriNet.Arc(arc.source, new_place)
        ocpn.add_arc(new_arc)
    # remove all old arcs
    while place.in_arcs:
        arc = next(iter(place.in_arcs))
        ocpn.remove_arc(arc)
    # remove old place
    ocpn.remove_place(place)

    return new_place


def remove_transition_and_connected_arcs(transition: ObjectCentricPetriNet.Transition, ocpn: ObjectCentricPetriNet):
    # checks for bugfixing
    if not transition in ocpn.transitions:
        raise Exception("Transition not in ocpn")

    ocpn.remove_arcs(list(transition.in_arcs.union(transition.out_arcs)))
    ocpn.remove_transition(transition)


@dataclass(frozen=True)
class FrozenMarking(object):
    '''
    Representing a Marking of an Object-Centric Petri Net.

    ...

    Attributes
    tokens: set(Tuple)

    Methods
    -------
    add_token(pl, obj):
        adds an object obj to a place pl
    '''
    _tokens: FrozenSet[Tuple[ObjectCentricPetriNet.Place, str]] = field(default_factory=frozenset)

    @property
    def tokens(self) -> FrozenSet[Tuple[ObjectCentricPetriNet.Place, str]]:
        return self._tokens


def display_memory_details_top(snapshot, key_type='lineno', limit=3):
    snapshot = snapshot.filter_traces((
        tracemalloc.Filter(False, "<frozen importlib._bootstrap>"),
        tracemalloc.Filter(False, "<unknown>"),
    ))
    top_stats = snapshot.statistics(key_type)

    print("Top %s lines" % limit)
    for index, stat in enumerate(top_stats[:limit], 1):
        frame = stat.traceback[0]
        # replace "/path/to/module/file.py" with "module/file.py"
        filename = os.sep.join(frame.filename.split(os.sep)[-2:])
        print("#%s: %s:%s: %.1f KiB"
              % (index, filename, frame.lineno, stat.size / 1024))
        line = linecache.getline(frame.filename, frame.lineno).strip()
        if line:
            print('    %s' % line)

    other = top_stats[limit:]
    if other:
        size = sum(stat.size for stat in other)
        print("%s other: %.1f KiB" % (len(other), size / 1024))
    total = sum(stat.size for stat in top_stats)
    print("Total allocated size: %.1f KiB" % (total / 1024))


def display_memory_total(snapshot, key_type='lineno'):
    top_stats = snapshot.statistics(key_type)
    total = sum(stat.size for stat in top_stats)
    print("Total allocated size: %.1f KiB" % (total / 1024))

def get_mem_total(snapshot, key_type='lineno'):
    top_stats = snapshot.statistics(key_type)
    total = sum(stat.size for stat in top_stats)
    return total

def create_evaluation_data(size_of_net, degree_of_parallel_transitions, fitness):
    # create de jure pn
    num_places = 0
    num_transitions = 0

    last_place = None

    sequential_transitions = math.floor(size_of_net * (1 - degree_of_parallel_transitions))
    parallel_transitions = size_of_net - sequential_transitions
    pn = ObjectCentricPetriNet(name="PN")

    p_initial = ObjectCentricPetriNet.Place(name=f"p{num_places}", object_type="T", initial=True)
    pn.places.add(p_initial)
    last_place = p_initial
    num_places += 1

    for i in range(sequential_transitions - 2):
        tr = ObjectCentricPetriNet.Transition(name=f"t{num_transitions}", label=f"t{num_transitions}")
        pn.transitions.add(tr)
        num_transitions += 1

        pn.add_arc(ObjectCentricPetriNet.Arc(last_place, tr))

        pl = ObjectCentricPetriNet.Place(name=f"p{num_places}", object_type="T")
        pn.places.add(pl)
        last_place = pl
        num_places += 1

        pn.add_arc(ObjectCentricPetriNet.Arc(tr, last_place))

    # last sequential
    tr = ObjectCentricPetriNet.Transition(name=f"t{num_transitions}", label=f"t{num_transitions}")
    pn.transitions.add(tr)
    num_transitions += 1

    last_transition = tr

    pn.add_arc(ObjectCentricPetriNet.Arc(last_place, tr))

    # sequential after parallel
    seq_after_parallel = ObjectCentricPetriNet.Transition(name=f"t{num_transitions + parallel_transitions}", label=f"t{num_transitions + parallel_transitions}")
    pn.transitions.add(seq_after_parallel)

    # prepare for parallel
    p_final = ObjectCentricPetriNet.Place(name=f"p{num_places + (2 * parallel_transitions)}", object_type="T", final=True)
    pn.places.add(p_final)

    for i in range(parallel_transitions):
        pl = ObjectCentricPetriNet.Place(name=f"p{num_places}", object_type="T")
        pn.places.add(pl)
        num_places += 1

        pn.add_arc(ObjectCentricPetriNet.Arc(last_transition, pl))

        tr = ObjectCentricPetriNet.Transition(name=f"t{num_transitions}", label=f"t{num_transitions}")
        pn.transitions.add(tr)
        num_transitions += 1

        pn.add_arc(ObjectCentricPetriNet.Arc(pl, tr))

        pl2 = ObjectCentricPetriNet.Place(name=f"p{num_places}", object_type="T")
        pn.places.add(pl2)
        num_places += 1

        pn.add_arc(ObjectCentricPetriNet.Arc(tr, pl2))
        pn.add_arc(ObjectCentricPetriNet.Arc(pl2, seq_after_parallel))

    pn.add_arc(ObjectCentricPetriNet.Arc(seq_after_parallel, p_final))

    # create log

    correct_events = math.floor(fitness * num_transitions)
    wrong_events = num_transitions - correct_events
    
    pre = """{
    "ocel:global-log": {
    "ocel:attribute-names": [],
    "ocel:object-types": [
    "T"
    ],
    "ocel:version": [
    "1.0"
    ],
    "ocel:ordering": [
    "timestamp"
    ]
    },
    "ocel:events": {
    """

    post = """},
    "ocel:objects": {
      "i1": {
    "ocel:type": "T",
    "ocel:ovmap": {}
    }
    }
    }"""

    event = """"x0": {
    "ocel:activity": "x1",
    "ocel:timestamp": "x2",
    "ocel:omap": [
    "i1"
    ],
    "ocel:vmap": {}
    },
    """

    last_event = """"x0": {
        "ocel:activity": "x1",
        "ocel:timestamp": "x2",
        "ocel:omap": [
        "i1"
        ],
        "ocel:vmap": {}
        }
        """

    date_to_use = datetime.now(timezone.utc)
    date_to_use.replace(microsecond=0)

    f = open("sample-logs/jsonocel/mylog.jsonocel", "w")
    f.write(pre)
    for i in range(num_transitions):
        if i <= correct_events:
            my_str = event
            my_str = my_str.replace("x0", f"{i}")
            my_str = my_str.replace("x1", f"t{i}")
            my_str = my_str.replace("x2", (date_to_use + timedelta(days=i)).isoformat(timespec="seconds"))
            f.write(my_str)
        else:
            my_str = event
            my_str = my_str.replace("x0", f"{i}")
            my_str = my_str.replace("x1", f"xt{i}")
            my_str = my_str.replace("x2", (date_to_use + timedelta(days=i)).isoformat(timespec="seconds"))
            f.write(my_str)

    my_str = last_event
    my_str = my_str.replace("x0", f"{num_transitions}")
    if correct_events == num_transitions:
        my_str = my_str.replace("x1", f"t{num_transitions}")
    else:
        my_str = my_str.replace("x1", f"xt{num_transitions}")
    my_str = my_str.replace("x2", (date_to_use + timedelta(days=num_transitions)).isoformat(timespec="seconds"))
    f.write(my_str)

    f.write(post)
    f.close()

    ocel = ocel_import_factory.apply("sample-logs/jsonocel/mylog.jsonocel")

    return pn, ocel
