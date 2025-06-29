from ocpa.algo.discovery.neo4j_discovery.discover_proclet_model import discover_proclet_model_neo4j
from ocpa.algo.discovery.neo4j_discovery.discover_dfg import discover_dfg_neo4j

# Example usage script for Neo4j-based discovery functions

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
