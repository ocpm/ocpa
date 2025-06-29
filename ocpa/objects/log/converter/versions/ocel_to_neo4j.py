from neomodel import (
    StructuredNode,
    StringProperty,
    DateTimeProperty,
    UniqueIdProperty,
    Relationship,
    RelationshipTo,
    config,
    db
)
from datetime import datetime
from collections import defaultdict
import pytz


class Entity(StructuredNode):
    oid = UniqueIdProperty()
    EntityType = StringProperty(index=True)
    Related = Relationship('Entity', 'RELATED')


class Event(StructuredNode):
    eid = UniqueIdProperty()
    Activity = StringProperty(index=True)
    Timestamp = DateTimeProperty(index=True)
    corr = RelationshipTo('Entity', 'CORR')
    df = RelationshipTo('Event', 'DF')


def ocel_to_neo4j(url, ocel):
    """
    Converts an OCEL (Object-Centric Event Log) into a Neo4j graph database.

    This function creates nodes for Entities and Events, and relationships
    between them:
    - CORR: Links Events to related Entities.
    - DF (Directly Follows): Links Events in order based on shared Entities.
    - RELATED: Links Entities that co-occur in the same Events.

    The graph schema:
    - Nodes:
        * Entity (oid, EntityType)
        * Event (eid, Activity, Timestamp)
    - Relationships:
        * (Event)-[:CORR]->(Entity)
        * (Event)-[:DF {ent_id, EntityType}]->(Event)
        * (Entity)-[:RELATED {count, event_ids}]-(Entity)

    Parameters:
    ----------
    url : str
        The Neo4j connection URL in the form 'bolt://user:password@host:port'.
    ocel : Ocel object
        The OCEL object containing event data, object data, and mappings.

    Returns:
    -------
    db : neomodel.db
        The Neo4j database connection object after populating the graph.
    """

    # Configure Neo4j connection
    config.DATABASE_URL = url
    # Clear the database before inserting new data
    db.cypher_query("MATCH (n) DETACH DELETE n")

    # Extract objects, events, and object-event mappings from the OCEL
    obj_ocel = ocel.obj.raw.objects
    events_ocel = ocel.obj.raw.events
    obj_event_mapping = ocel.obj.raw.obj_event_mapping

    # Create reverse mapping: event -> list of objects
    event_obj_mapping = {}
    for obj_id, event_ids in obj_event_mapping.items():
        for event_id in event_ids:
            if event_id not in event_obj_mapping:
                event_obj_mapping[event_id] = []
            event_obj_mapping[event_id].append(obj_id)

    batch_size = 500  # Batch size for Cypher queries

    # ---------------------------
    # 1. Insert Entity nodes
    # ---------------------------
    entity_rows = [{'oid': obj.id, 'EntityType': obj.type} for obj in obj_ocel.values()]
    entity_query = """
    UNWIND $rows AS row
    MERGE (e:Entity {oid: row.oid})
    SET e.EntityType = row.EntityType
    """
    for i in range(0, len(entity_rows), batch_size):
        db.cypher_query(entity_query, {'rows': entity_rows[i:i + batch_size]})

    # ---------------------------
    # 2. Insert Event nodes
    # ---------------------------
    event_rows = [
        {
            'eid': eid,
            'activity': ev.act,
            'timestamp': ev.time.replace(tzinfo=pytz.UTC)  # Ensure UTC timezone
        }
        for eid, ev in events_ocel.items()
    ]
    event_query = """
    UNWIND $rows AS row
    MERGE (e:Event {eid: row.eid})
    SET e.activity = row.activity, e.timestamp = row.timestamp
    """
    for i in range(0, len(event_rows), batch_size):
        db.cypher_query(event_query, {'rows': event_rows[i:i + batch_size]})

    # ---------------------------
    # 3. Create CORR relationships (Event -> Entity)
    # ---------------------------
    corr_rows = []
    for eid, oids in event_obj_mapping.items():
        for oid in oids:
            corr_rows.append({'eid': eid, 'oid': oid})

    corr_query = """
    UNWIND $rows AS row
    MATCH (e:Event {eid: row.eid})
    MATCH (o:Entity {oid: row.oid})
    MERGE (e)-[:CORR]->(o)
    """
    for i in range(0, len(corr_rows), batch_size):
        db.cypher_query(corr_query, {'rows': corr_rows[i:i + batch_size]})

    # ---------------------------
    # 4. Create DF (Directly Follows) relationships between events
    # ---------------------------

    # Step 1: Group events by entity
    entity_events = {}
    for oid in obj_ocel:
        entity_events[oid] = []

    # Build list of (event_id, timestamp) pairs for each entity
    for eid, ev in events_ocel.items():
        for oid in event_obj_mapping.get(eid, []):
            entity_events[oid].append((eid, ev.time))

    # Step 2: For each entity, sort events by timestamp and create DF relationships
    follows_rel_rows = []
    for oid, events in entity_events.items():
        if len(events) < 2:
            continue  # No DF relationship needed if only one event

        # Sort events by timestamp
        sorted_events = sorted(events, key=lambda x: x[1])

        # Create consecutive pairs of events
        for i in range(len(sorted_events) - 1):
            e1_id, e1_time = sorted_events[i]
            e2_id, e2_time = sorted_events[i + 1]

            follows_rel_rows.append({
                'src': e1_id,
                'dst': e2_id,
                'ent_id': oid,
                'EntityType': obj_ocel[oid].type
            })

    follows_query = """
    UNWIND $rows AS row
    MATCH (e1:Event {eid: row.src})
    MATCH (e2:Event {eid: row.dst})
    MERGE (e1)-[r:DF]->(e2)
    SET r.ent_id = row.ent_id, r.EntityType = row.EntityType
    """

    for i in range(0, len(follows_rel_rows), batch_size):
        db.cypher_query(follows_query, {'rows': follows_rel_rows[i:i + batch_size]})

    # ---------------------------
    # 5. Create RELATED relationships between Entities
    # ---------------------------

    # Step 1: Find entity pairs that co-occur in the same event
    cooccurrence_pairs = defaultdict(set)
    for eid, oids in event_obj_mapping.items():
        for i in range(len(oids)):
            for j in range(i + 1, len(oids)):
                oid1, oid2 = oids[i], oids[j]
                # Create canonical ordering to avoid duplicate pairs (A,B) and (B,A)
                if oid1 < oid2:
                    pair = (oid1, oid2)
                else:
                    pair = (oid2, oid1)
                cooccurrence_pairs[pair].add(eid)

    # Step 2: Create RELATED relationships with metadata (count and event_ids)
    related_rows = []
    for (oid1, oid2), events in cooccurrence_pairs.items():
        related_rows.append({
            'oid1': oid1,
            'oid2': oid2,
            'count': len(events),  # Number of co-occurrences
            'event_ids': list(events)  # List of event IDs where both entities co-occur
        })

    related_query = """
    UNWIND $rows AS row
    MATCH (e1:Entity {oid: row.oid1})
    MATCH (e2:Entity {oid: row.oid2})
    MERGE (e1)-[r:RELATED]-(e2)
    SET r.count = row.count, r.event_ids = row.event_ids
    """
    for i in range(0, len(related_rows), batch_size):
        db.cypher_query(related_query, {'rows': related_rows[i:i + batch_size]})

    # ---------------------------
    # Print summary of created graph
    # ---------------------------
    print('Graph created with:')
    print(f"- Entities: {len(entity_rows)}")
    print(f"- Events: {len(event_rows)}")
    print(f"- CORR relationships: {len(corr_rows)}")
    print(f"- DF relationships: {len(follows_rel_rows)}")
    print(f"- RELATED relationships: {len(related_rows)}")

    return db
