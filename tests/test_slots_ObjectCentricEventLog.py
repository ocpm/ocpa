import timeit
from datetime import datetime
from functools import partial

from ocpa.objects.log.variants.obj import (
    Event,
    MetaObjectCentricData,
    Obj,
    ObjectCentricEventLog,
    RawObjectCentricData,
)


def set_get_delete_event(e: Event):
    e.omap = ["o1", "o2", "i3"]
    e.omap
    del e.omap
    e.act = "Test Slots"
    e.act
    del e.act


def set_get_delete_obj(o: Obj):
    o.ovmap = {"price": 30.0, "discount": 25.0}
    o.ovmap
    del o.ovmap
    o.type = "sales order"
    o.type
    del o.type


def main():
    event = Event(
        id="1",
        act="Test Speed",
        time=datetime.today(),
        omap=["o1", "i1"],
        vmap={"resource": "Tim"},
    )
    obj = Obj(id="o1", type="order", ovmap={"price": 30.0})

    speed_event = min(
        timeit.repeat(partial(set_get_delete_event, event), number=10_000_000)
    )
    speed_obj = min(timeit.repeat(partial(set_get_delete_obj, obj), number=10_000_000))

    print(f"Speed of Event class with slots: {speed_event}")
    print()
    print(f"Speed of Obj class with slots: {speed_obj}")


main()
