from ocpa.objects.log.obj import OCEL


def filter_cases(ocel, cases):
    events = [e for case in cases for e in case]
    new_event_df = ocel.log[ocel.log["event_id"].isin(events)].copy()
    new_log = OCEL(new_event_df, object_types=ocel.object_types, execution_extraction=ocel._execution_extraction,
                   leading_object_type=ocel._leading_type, variant_extraction=ocel._variant_extraction)
    return new_log