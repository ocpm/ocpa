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

def discover_proclet_model_neo4j(url):
    """
    Discover and construct a proclet model from a Neo4j event log database.

    This function connects to the specified Neo4j database URL and performs a series of 
    Cypher queries to:
    1. Create Class nodes representing unique combinations of activities and entity types.
    2. Link events to their corresponding Class nodes with OBSERVED relationships.
    3. Create DF_C (directly-follows constrained) relationships between classes based on 
       direct event flows that share the same entity instance.
    4. Create SYNC relationships between classes that share the same activity but belong 
       to different entity types.
    5. Retrieve the full proclet model consisting of classes, DF_C, and SYNC relationships.

    Args:
        url (str): The Neo4j database URL.

    Returns:
        proclet_neo (tuple): The result of the Cypher query that retrieves the proclet model, 
                             containing class nodes and their relationships.
    """
    # Set the Neo4j database URL for the connection
    config.DATABASE_URL = url

    # Query 1: Create Class nodes for each unique combination of activity and entity type
    db.cypher_query("""
        MATCH (e:Event)-[:CORR]->(n:Entity) 
        WITH DISTINCT e.activity AS actName, n.EntityType AS EType
        MERGE (c:Class { 
            ID: actName + "_" + EType, 
            Name: actName, 
            EntityType: EType, 
            Type: "activity,EntityType"
        })
    """)

    # Query 2: Create OBSERVED relationships from Events to their corresponding Class nodes
    db.cypher_query("""
        MATCH (c:Class) 
        WHERE c.Type = "activity,EntityType"
        MATCH (e:Event)-[:CORR]->(n:Entity)
        WHERE c.Name = e.activity AND c.EntityType = n.EntityType
        CREATE (e)-[:OBSERVED]->(c)
    """)

    # Query 3: Create DF_C relationships between Class nodes 
    # based on directly-follows relationships within the same entity instance
    db.cypher_query("""
        MATCH (c1:Class)<-[:OBSERVED]-(e1:Event)-[df:DF]->(e2:Event)-[:OBSERVED]->(c2:Class)
        MATCH (e1)-[:CORR]->(n)<-[:CORR]-(e2)
        WHERE 
            c1.Type = c2.Type AND 
            n.EntityType = df.EntityType AND
            c1.EntityType = n.EntityType AND
            c2.EntityType = n.EntityType
        WITH n.EntityType AS EType, c1, COUNT(df) AS df_freq, c2
        MERGE (c1)-[rel2:DF_C {EntityType: EType}]->(c2)
        ON CREATE SET rel2.count = df_freq
    """)

    # Query 4: Create SYNC relationships between Class nodes
    # that represent the same activity but different entity types
    db.cypher_query("""
        MATCH (c1:Class), (c2:Class) 
        WHERE 
            c1.Name = c2.Name AND 
            c1.EntityType <> c2.EntityType
        MERGE (c1)-[:SYNC]->(c2)
    """)

    # Query 5: Retrieve the proclet model including Class nodes,
    # DF_C relationships, and SYNC relationships
    proclet_neo = db.cypher_query("""
        MATCH (c1:Class) 
        WHERE c1.Type = "activity,EntityType"
        OPTIONAL MATCH (c1)-[df:DF_C]->(c2)
        WHERE c1.Type = c2.Type
        OPTIONAL MATCH (c1)-[sync:SYNC]->(c3)
        WHERE c1.Type = c3.Type
        RETURN c1, df, c2, sync, c3
    """)

    return proclet_neo
