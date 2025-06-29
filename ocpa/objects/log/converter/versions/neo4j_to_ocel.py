from ocpa.objects.log.converter.versions.ocel_to_neo4j import Entity, Event
from neomodel import (db, config, StructuredNode, StringProperty, IntegerProperty,
                      UniqueIdProperty, RelationshipTo, DateTimeProperty, Relationship)
from collections import defaultdict
import pandas as pd
from ocpa.objects.log.util import misc as log_util


def neo4j_to_ocel(url):
    """
    Converts an event log stored in a Neo4j database (using the OCEL data model) into an OCEL object in Python.

    Args:
        url (str): The Neo4j database URL in the format 'bolt://username:password@host:port'.

    Returns:
        OCEL object: An OCEL log object generated from the Neo4j database.

    The function performs the following steps:
    1. Connects to the Neo4j database using neomodel.
    2. Queries events, objects, and their correlations.
    3. Builds an event log dataframe with associated objects.
    4. Converts the dataframe into an OCEL object for further processing or analysis.
    """

    # Set neomodel database URL
    config.DATABASE_URL = url

    # Helper function to convert Neo4j datetime to native Python datetime
    def convert_neo4j_datetime(neo_time):
        return neo_time.to_native() if hasattr(neo_time, "to_native") else neo_time

    # Query all events from the Neo4j database
    results_events, _ = db.cypher_query("MATCH (e:Event) RETURN e")

    # Query all objects with their IDs and types
    results_object_types, _ = db.cypher_query("""
        MATCH (o:Entity)
        RETURN o.oid AS oid, o.EntityType AS type
    """)

    # Query all object-event correlations
    results_o_e_mapping, _ = db.cypher_query("""
        MATCH (e:Event)-[:CORR]->(o:Entity)
        RETURN o.oid AS object_id, e.eid AS event_id
    """)

    # Build a mapping from object ID to its type
    object_id_to_type = {record[0]: record[1] for record in results_object_types}
    object_types = set(object_id_to_type.values())  # Get all unique object types

    # Build a mapping from event_id to {object_type: [list of object_ids]}
    event_to_objects_by_type = defaultdict(lambda: defaultdict(list))
    for record in results_o_e_mapping:
        obj_id, event_id = record
        obj_type = object_id_to_type.get(obj_id)
        if obj_type:
            event_to_objects_by_type[event_id][obj_type].append(obj_id)

    # Construct event dataframe with event_id, activity, and timestamp
    event_rows = []
    for record in results_events:
        node = record[0]
        event_rows.append({
            "event_id": node['eid'],
            "event_activity": node['activity'],
            "event_timestamp": convert_neo4j_datetime(node['timestamp']),
        })

    events_df = pd.DataFrame(event_rows)
    events_df['event_start_timestamp'] = events_df['event_timestamp']  # Duplicate column for start timestamp

    # Add columns for each object type containing lists of associated object IDs
    for obj_type in object_types:
        events_df[obj_type] = events_df['event_id'].apply(
            lambda eid: event_to_objects_by_type.get(eid, {}).get(obj_type, [])
        )

    # Prepare dataframe: set index, sort, and ensure event_id is a column
    events_df = events_df.set_index('event_id')
    events_df['event_id'] = events_df.index
    events_df = events_df.sort_index()

    # Define parameters for OCEL conversion
    parameters = {
        "obj_names": list(object_types),  # List of object types
        "val_names": [],  # No additional attribute columns
        "act_name": "event_activity",  # Column name for activity
        "time_name": "event_timestamp",  # Column name for timestamp
        "sep": ","  # Separator for multi-valued fields
    }

    # Create OCEL log from dataframe
    new_ocel = log_util.copy_log_from_df(events_df, parameters)

    return new_ocel
