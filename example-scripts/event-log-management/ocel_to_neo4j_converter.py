# Import necessary functions for loading OCEL logs and uploading to Neo4j
from ocpa.objects.log.importer.ocel import factory as ocel_import_factory
from ocpa.objects.log.converter.versions..ocel_to_neo4j import ocel_to_neo4j

# Specify the path to the OCEL log file
# This file contains the event data and object relationships in JSON-OCEL format
filename = "../../sample_logs/jsonocel/exported-p2p-normal.jsonocel"

# Load the OCEL log into a Python object
# The 'ocel' object now holds events, objects, and their relations for further processing
ocel = ocel_import_factory.apply(filename)

# Define the connection URL to the Neo4j database
# Format: 'bolt://<username>:<password>@<host>:<port>'
# Example: 'bolt://neo4j:neo4jpass@localhost:7687'
url = 'bolt://neo4j:neo4jpass@localhost:7687'

# Upload the OCEL event log into the Neo4j database
# This converts the OCEL structure into nodes (events, objects) and relationships in the graph database
# The returned 'db' object represents the connection to Neo4j, allowing further queries if needed. 
# Importing classes Entity and Events is necessary for cypher querying.
db = ocel_to_neo4j(url, ocel)
