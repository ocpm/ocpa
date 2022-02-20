
def number_of_objects(node,ocel):
    return len(ocel.get_value(node.event_id,"event_objects"))
    #return len(ocel.log.loc[node.event_id]["event_objects"])

