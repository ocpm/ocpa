import pandas as pd
from lxml import etree, objectify
from datetime import datetime
from ocpa.objects.log.ocel import OCEL


def parse_xml(value, tag_str_lower):
    if "float" in tag_str_lower:
        return float(value)
    elif "date" in tag_str_lower:
        return datetime.fromisoformat(value)
    return str(value)


def apply(file_path, return_obj_df=None, parameters=None, file_path_object_attribute_table = None) -> OCEL:
    if parameters is None:
        parameters = {}

    if 'return_df' in parameters:
        return_df = parameters['return_df']
    else:
        return_df = False

    if 'return_obj_df' in parameters:
        return_obj_df = parameters['return_obj_df']
    else:
        return_obj_df = None

    if return_df:
        parser = etree.XMLParser(remove_comments=True)
        tree = objectify.parse(file_path, parser=parser)
        root = tree.getroot()

        eve_stream = []
        obj_stream = []
        obj_types = {}

        for child in root:
            if child.tag.lower().endswith("events"):
                for event in child:
                    eve = {}
                    for child2 in event:
                        if child2.get("key") == "id":
                            eve["event_id"] = child2.get("value")
                        elif child2.get("key") == "timestamp":
                            eve["event_timestamp"] = datetime.fromisoformat(
                                child2.get("value"))
                        elif child2.get("key") == "activity":
                            eve["event_activity"] = child2.get("value")
                        elif child2.get("key") == "omap":
                            omap = []
                            for child3 in child2:
                                omap.append(child3.get("value"))
                            eve["@@omap"] = omap
                        elif child2.get("key") == "vmap":
                            for child3 in child2:
                                eve["event_" + child3.get("key")] = parse_xml(
                                    child3.get("value"), child3.tag.lower())
                    eve_stream.append(eve)

            elif child.tag.lower().endswith("objects"):
                for object in child:
                    obj = {}
                    for child2 in object:
                        if child2.get("key") == "id":
                            obj["object_id"] = child2.get("value")
                        elif child2.get("key") == "type":
                            obj["object_type"] = child2.get("value")
                        elif child2.get("key") == "ovmap":
                            for child3 in child2:
                                obj["object_" + child3.get("key")] = parse_xml(
                                    child3.get("value"), child3.tag.lower())
                    obj_stream.append(obj)

        for obj in obj_stream:
            obj_types[obj["object_id"]] = obj["object_type"]

        for eve in eve_stream:
            for obj in eve["@@omap"]:
                ot = obj_types[obj]
                if not ot in eve:
                    eve[ot] = []
                eve[ot].append(obj)
            del eve["@@omap"]

        eve_df = pd.DataFrame(eve_stream)
        obj_df = pd.DataFrame(obj_stream)
        eve_df["event_id"] = eve_df["event_id"].astype(float).astype(int)
        # eve_df.type = "succint"

        #eve_df.type = "succint"

        if return_obj_df or (return_obj_df is None and len(obj_df.columns) > 1):
            return eve_df, obj_df
        return eve_df
    else:
        raise ValueError(
            "Returning ocel from xml is not supported yet. Use return_df=True.")
