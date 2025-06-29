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

def discover_dfg_neo4j(url):
    """
    Constructs and retrieves a Directly Follows Graph (DFG) from event logs stored 
    in a Neo4j database.

    This function performs the following steps:
    1. Creates unique Activity Class nodes for each distinct activity in the event log.
    2. Links each Event node to its corresponding Activity Class node via an 'OBSERVED' relationship.
    3. Builds 'DF_C' (Directly Follows Class) relationships between Activity Class nodes, 
       representing the directly-follows behavior aggregated from the event-level 
       directly-follows (DF) relationships. These relationships are annotated with 
       frequency counts and entity types.
    4. Retrieves the DFG, which consists of Activity Class nodes and the 'DF_C' 
       relationships between them.

    Args:
        url (str): The Neo4j database connection URL.

    Returns:
        list: A list containing the result of the Cypher query that retrieves the DFG. 
              Each entry includes:
              - Source Activity Class node (c1)
              - Directly-follows relationship (df) with frequency count and entity type
              - Target Activity Class node (c2)

    Note:
        This function assumes the existence of 'Event' nodes with attributes 'activity' 
        and 'EntityType', as well as 'DF' (Directly Follows) relationships between events, 
        and 'CORR' relationships that define entity correlation (e.g., case or object type).
    """
    
    # Set the Neo4j database connection URL
    config.DATABASE_URL = url
    
    # Query 1: Create unique Activity Class nodes based on distinct event activity names
    db.cypher_query("""
        MATCH (e:Event)
        WITH DISTINCT e.activity AS actName
        MERGE (c:Class {Name: actName, Type: "Activity", ID: actName})
    """)
    
    # Query 2: Connect each Event node to its corresponding Activity Class node
    db.cypher_query("""
        MATCH (c:Class) WHERE c.Type = "Activity"
        MATCH (e:Event) WHERE c.Name = e.activity
        CREATE (e)-[:OBSERVED]->(c)
    """)
    
    # Query 3: Create directly-follows relationships (DF_C) between Activity Class nodes
    # The relationship includes a frequency count of how often one activity directly follows another
    db.cypher_query("""
        MATCH (c1:Class)<-[:OBSERVED]-(e1:Event)-[df:DF]->(e2:Event)-[:OBSERVED]->(c2:Class)
        MATCH (e1)-[:CORR]->(n)<-[:CORR]-(e2)
        WHERE c1.Type = c2.Type AND n.EntityType = df.EntityType
        WITH n.EntityType as EntityType, c1, count(df) AS df_freq, c2
        MERGE (c1)-[rel2:DF_C {EntityType:EntityType}]->(c2)
        ON CREATE SET rel2.count = df_freq
    """)
    
    # Query 4: Retrieve the Directly Follows Graph (DFG) as relationships between Activity Class nodes
    dfg_neo = db.cypher_query("""
        MATCH (c1:Class) WHERE c1.Type = "Activity"
        OPTIONAL MATCH (c1)-[df:DF_C]->(c2)
        RETURN c1, df, c2
    """)
    
    # Return the DFG result
    return dfg_neo
