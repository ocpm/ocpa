import networkx as nx
def calculate(EOG):
    preset = {}
    i = 0
    for e in EOG.nodes:
        if i%10 == 0:
            print("Event "+str(i))
        i+=1
        preset[e] = list(nx.ancestors(EOG,e))
        #USE THIS FOR LARGE EVENT LOGS
        #stable speed also for later events, large logs with large connected components
        #preset[e] = [v for v in nx.dfs_predecessors(EOG, source=e).keys() if v!=e]
        #fast for small graphs/no connected component
        #preset[e] = [n for n in nx.traversal.bfs_tree(EOG, e, reverse=True) if n != e]
    return preset