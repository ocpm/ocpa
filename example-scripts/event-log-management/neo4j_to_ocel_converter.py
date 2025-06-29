# Import the function to convert Neo4j data back into an OCEL log
from ocpa.objects.log.converter.versions.neo4j_to_ocel import neo4j_to_ocel

# Specify the Neo4j connection URL
# Format: 'bolt://<username>:<password>@<host>:<port>'
# Example assumes Neo4j is running locally with username 'neo4j' and password 'password'
url = 'bolt://neo4j:password@localhost:7687'

# Retrieve the OCEL event log from the Neo4j database
# This function queries the graph stored in Neo4j and reconstructs the OCEL event log,
# including events, objects, and their relationships.
ocel_from_neo4j = neo4j_to_ocel(url)

# The 'ocel_from_neo4j' object now holds the event log in OCEL format.
