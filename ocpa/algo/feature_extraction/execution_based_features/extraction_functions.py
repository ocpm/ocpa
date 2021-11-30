def number_of_events(case,ocel):
    return len(case.nodes)

def number_of_ending_events(case,ocel):
    return len([n for n in case.nodes if len(list(case.out_edges(n)))==0 ])