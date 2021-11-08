from ocpa.objects.log.obj import OCEL


def generalize(ocel, generalization_mapping):
    sublog = ocel.log.copy()
    object_types = ocel.object_types
    for ot in object_types:
            sublog[ot] = sublog[ot].apply(tuple) 
    for mapping in generalization_mapping:
        sublog['group'] = range(0,len(sublog))
        sublog.loc[sublog["event_activity"].isin(mapping[0]),"group"] = -1
        sublog.loc[sublog.duplicated(subset = object_types+["group"], keep = False),"event_activity"]=mapping[1]
        sublog = sublog.drop_duplicates(subset = object_types+["group"],keep="first")
    for ot in object_types:
        sublog[ot] = sublog[ot].apply(list) 
    sublog = sublog.drop(columns=["group"])
    return OCEL(sublog, object_types=ocel.object_types)