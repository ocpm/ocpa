Neo4j Discovery Functions
=========================

This document explains the usage of the Neo4j-based discovery functions
available in the `ocpa.algo.discovery.neo4j_discovery` module:

- `discover_proclet_model_neo4j`
- `discover_dfg_neo4j`

These functions enable discovery of process models directly from event logs stored in a Neo4j database.

Usage Example
-------------

.. code-block:: python

    from ocpa.algo.discovery.neo4j_discovery.discover_proclet_model import discover_proclet_model_neo4j
    from ocpa.algo.discovery.neo4j_discovery.discover_dfg import discover_dfg_neo4j

    # Define Neo4j connection URL
    url = 'bolt://neo4j:neo4jpass@localhost:7687'

    # Discover Proclet model from Neo4j
    proclet_neo = discover_proclet_model_neo4j(url)
    print("Proclet model discovered from Neo4j:")
    print(proclet_neo)

    # Discover Directly Follows Graph (DFG) from Neo4j
    dfg_neo = discover_dfg_neo4j(url)
    print("\nDirectly Follows Graph (DFG) discovered from Neo4j:")
    print(dfg_neo)


Neo4j Queries for Visual Inspection
-----------------------------------

After running the discovery functions, you can also execute the following Cypher queries
directly in your Neo4j database to visually inspect the discovered models.

1. Proclet Model Query
~~~~~~~~~~~~~~~~~~~~~~

This query retrieves activity and entity type classes, their directly-follows relationships, 
and synchronization relationships from the Neo4j database:

.. code-block:: cypher

    MATCH (c1:Class) 
    WHERE c1.Type = "activity,EntityType"
    OPTIONAL MATCH (c1)-[df:DF_C]->(c2)
    WHERE c1.Type = c2.Type
    OPTIONAL MATCH (c1)-[sync:SYNC]->(c3)
    WHERE c1.Type = c3.Type
    RETURN c1, df, c2, sync, c3


2. Directly Follows Graph (DFG) Query
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This query retrieves activity classes and their directly-follows relationships:

.. code-block:: cypher

    MATCH (c1:Class) WHERE c1.Type = "Activity"
    OPTIONAL MATCH (c1)-[df:DF_C]->(c2)
    RETURN c1, df, c2


Notes
-----

- The `url` parameter should point to your running Neo4j instance, including username and password.
- The discovered models are returned as query results that can be further processed or visualized.
- The Cypher queries provided are useful for manual inspection within the Neo4j Browser or other visualization tools.

