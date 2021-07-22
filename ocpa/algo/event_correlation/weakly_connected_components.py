import networkx as nx
def project_subgraph_on_activity(v_g,log):
    #grpah mit aktivitäten
    mapping = dict(zip(log["event_id"], log["event_activity"]))
    return nx.relabel_nodes(v_g,mapping)

def from_eog(EOG, ocel):   
    variants_dict = dict()
    case_graphs = sorted(nx.weakly_connected_components(EOG), key=len, reverse=True)
    case_id = 0
    for v_g in case_graphs:
        case = project_subgraph_on_activity(EOG.subgraph(v_g),ocel)
        variant = sorted(list(nx.generate_edgelist(case)))
        variant_string = ','.join(variant)
        if variant_string not in variants_dict:
            variants_dict[variant_string] = []
        variants_dict[variant_string].append(case_id)
        case_id +=1
    variant_frequencies = {v:len(variants_dict[v])/len(case_graphs) for v in variants_dict.keys()}
    variants, v_freq_list = map(list,zip(*sorted(list(variant_frequencies.items()),key = lambda x:x[1], reverse = True)))
    for v_id in range(0,len(variants)):
        v = variants[v_id]
        cases = [case_graphs[c_id] for c_id in variants_dict[v] ]
        events = list(set().union(*cases))
        ocel.loc[ocel["event_id"].isin(events),"event_variant"] = v_id
    ocel["event_variant"] = ocel["event_variant"].astype(int)
    return ocel, variants, v_freq_list


    