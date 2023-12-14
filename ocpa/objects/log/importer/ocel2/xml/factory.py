from typing import Optional, Dict, Any, List
from datetime import datetime
from lxml import etree, objectify
import pandas as pd
import networkx as nx

from ocpa.objects.log.ocel import OCEL
from ocpa.objects.log.variants.table import Table
from ocpa.objects.log.variants.graph import EventGraph
from ocpa.objects.log.variants.object_graph import ObjectGraph
from ocpa.objects.log.variants.object_change_table import ObjectChangeTable
import ocpa.objects.log.variants.util.table as table_utils
import ocpa.objects.log.converter.versions.df_to_ocel as obj_converter

EVENT_ID = "event_id"
EVENT_ACTIVITY = "event_activity"
EVENT_TIMESTAMP = "event_timestamp"
OBJECT_ID = "object_id"
OBJECT_TYPE = "object_type"
QUALIFIER = "qualifier"
CHANGED_FIELD = "chngfield"


def parse_xml(value, tag_str_lower):
    if "float" in tag_str_lower:
        return float(value)
    elif "date" in tag_str_lower:
        return datetime.fromisoformat(value)
    return str(value)


def process_object_types(child, object_type_attributes):
    for object_type in child:
        object_type_name = object_type.get("name")
        object_type_attributes[object_type_name] = {}
        for attributes in object_type:
            for attribute in attributes:
                attribute_name = attribute.get("name")
                attribute_type = attribute.get("type")
                object_type_attributes[object_type_name][attribute_name] = attribute_type


def process_event_types(child, event_type_attributes):
    for event_type in child:
        event_type_name = event_type.get("name")
        event_type_attributes[event_type_name] = {}
        for attributes in event_type:
            for attribute in attributes:
                attribute_name = attribute.get("name")
                attribute_type = attribute.get("type")
                event_type_attributes[event_type_name][attribute_name] = attribute_type

def process_objects(child, object_type_changes, obj_type_dict, o2o_graph, object_type_attributes):
    object_id = None
    object_type = None
    for obj in child:
        object_id = obj.get("id")
        object_type = obj.get("type")
        if object_type not in object_type_changes:
            object_type_changes[object_type] = []
        obj_type_dict[object_id] = object_type
        if object_id not in o2o_graph.nodes:
            o2o_graph.add_node(object_id)
        for child2 in obj:
            process_object_children(child2, object_type_changes, object_type, object_id, obj_type_dict, o2o_graph, object_type_attributes)

def process_object_children(child2, object_type_changes, object_type, object_id, obj_type_dict, o2o_graph, object_type_attributes):
    if child2.tag.endswith("objects"):
        process_target_objects(child2, object_id, obj_type_dict, o2o_graph)
    elif child2.tag.endswith("attributes"):
        process_object_attributes(child2, object_type_changes, object_type, object_id, object_type_attributes)

def process_target_objects(child2, object_id, obj_type_dict, o2o_graph):
    for target_object in child2:
        target_object_id = target_object.get("object-id")
        qualifier = target_object.get("qualifier")
        if object_id not in o2o_graph.nodes:
            o2o_graph.add_node(target_object_id)
        o2o_graph.add_edge(object_id, target_object_id, qualifier=qualifier)

def process_object_attributes(child2, object_type_changes, object_type, object_id, object_type_attributes):
    for attribute in child2:
        attribute_name = attribute.get("name")
        attribute_time = attribute.get("time")
        try:
            attribute_type = object_type_attributes[object_type][attribute_name]
        except:
            attribute_type = "string"
        attribute_text = parse_xml(attribute.text, attribute_type)
        if attribute_time == "0":
            object_type_changes[object_type].append(
                {OBJECT_ID: object_id, attribute_name: attribute_text, CHANGED_FIELD: attribute_name, EVENT_TIMESTAMP: attribute_time}
            )
        else:
            attribute_time = datetime.fromisoformat(attribute_time)
            object_type_changes[object_type].append(
                {OBJECT_ID: object_id, attribute_name: attribute_text, CHANGED_FIELD: attribute_name, EVENT_TIMESTAMP: attribute_time}
            )

def process_events(child, events_list, obj_type_dict, qualifier_dict, event_type_attributes):
    event_id = None
    event_type = None
    event_time = None

    for event in child:
        event_id = event.get("id")
        event_type = event.get("type")
        event_time = datetime.fromisoformat(event.get("time"))

        ev_dict = {EVENT_ID: event_id, EVENT_ACTIVITY: event_type, EVENT_TIMESTAMP: event_time}
        qualifier_dict[event_id] = {}
        for child2 in event:
            if child2.tag.endswith("objects"):
                process_event_objects(child2, ev_dict, obj_type_dict, qualifier_dict)
            elif child2.tag.endswith("attributes"):
                process_event_attributes(child2, ev_dict, event_type, event_type_attributes)

        events_list.append(ev_dict)

def process_event_objects(child2, ev_dict, obj_type_dict, qualifier_dict):
    for target_object in child2:
        target_object_id = target_object.get("object-id")
        qualifier_dict[ev_dict[EVENT_ID]][target_object_id] = target_object.get("qualifier")
        if obj_type_dict[target_object_id] in ev_dict:
            ev_dict[obj_type_dict[target_object_id]].append(target_object_id)
        else:
            ev_dict[obj_type_dict[target_object_id]] = [target_object_id]

def process_event_attributes(child2, ev_dict, event_type, event_type_attributes):
    for attribute in child2:
        attribute_name = attribute.get("name")
        attribute_name = "event_" + attribute_name
        attribute_text = attribute.text
        try:
            attribute_type = event_type_attributes[event_type][attribute_name]
        except:
            attribute_type = "string"
            ev_dict[attribute_name] = parse_xml(attribute_text, attribute_type)



def apply(file_path: str, parameters: Optional[Dict[Any, Any]] = None) -> OCEL:
    print(file_path)
    if parameters is None:
        parameters = {}

    events_list = []
    obj_type_dict = {}
    qualifier_dict = {}
    o2o_graph = nx.DiGraph()
    object_type_changes = {}

    parser = etree.XMLParser(remove_comments=True)
    tree = objectify.parse(file_path, parser=parser)
    root = tree.getroot()

    object_type_attributes = {}
    event_type_attributes = {}

    for child in root:
        if child.tag.endswith("object-types"):
            process_object_types(child, object_type_attributes)
        elif child.tag.endswith("event-types"):
            process_event_types(child, event_type_attributes)
        elif child.tag.endswith("objects"):
            process_objects(child, object_type_changes, obj_type_dict, o2o_graph, object_type_attributes)
        elif child.tag.endswith("events"):
            process_events(child, events_list, obj_type_dict, qualifier_dict, event_type_attributes)

    event_df = pd.DataFrame(events_list) if events_list else None
    event_df = event_df.fillna('')

    if "obj_names" not in parameters:
        parameters["obj_names"] = [c for c in event_df.columns if not c.startswith("event_")]

    log = Table(event_df, parameters=parameters)
    obj = obj_converter.apply(event_df)
    graph = EventGraph(table_utils.eog_from_log(log, qualifier_dict))
    o2o_graph = ObjectGraph(o2o_graph)
    for object_type in object_type_changes:
        object_type_changes[object_type] = pd.DataFrame(object_type_changes[object_type])
    change_table = ObjectChangeTable(object_type_changes)
    ocel = OCEL(log, obj, graph, parameters, o2o_graph, change_table)
    return ocel
