from dataclasses import dataclass
from ocpa.objects.log.variants.obj import ObjectCentricEventLog
from ocpa.objects.log.variants.graph import EventGraph
from ocpa.objects.log.variants.table import Table


@dataclass
class OCEL:
    log: Table
    obj: ObjectCentricEventLog
    graph: EventGraph

    # _get_case_objects
    @property
    def case_objects(self):
        pass

    # _get_cases
    @property
    def cases(self):
        pass

    # _get_case_mappings
    @property
    def case_mappings(self):
        pass

    # _get_variants
    @property
    def variants(self):
        pass

    # _get_variant_frequency
    @property
    def variant_frequencies(self):
        pass

    # _get_variant_graphs
    @property
    def variant_graphs(self):
        pass

    # _get_object_types
    @property
    def object_types(self):
        pass

    # _get_variants_dict
    @property
    def variants_dict(self):
        pass


class old_OCEL():
    def __init__(self, log, object_types=None, precalc=False, execution_extraction="weakly", leading_object_type="order", variant_extraction="complex", variant_timeout=3600):
        self._log = log
        self._log["event_index"] = self._log["event_id"]
        self._log = self._log.set_index("event_index")
        #self._event_mapping =  dict(zip(ocel["event_id"], ocel["event_objects"]))
        self._execution_extraction = execution_extraction
        self._leading_type = leading_object_type
        self._variant_extraction = variant_extraction
        self._variant_timeout = variant_timeout
        if object_types != None:
            self._object_types = object_types
        else:

            self._object_types = [
                c for c in self._log.columns if not c.startswith("event_")]
        # clean empty events
        self.clean_empty_events()
        self.create_efficiency_objects()
        #self._log = self._log[self._log.apply(lambda x: any([len(x[ot]) > 0 for ot in self._object_types]))]
        if precalc:
            self._eog = self.eog_from_log()
            self._cases, self._case_objects, self._case_mappings = self.calculate_cases()
            self._variants, self._variant_frequency, self._variant_graphs, self._variants_dict = self.calculate_variants()
        else:
            self._eog = None
            self._cases = None
            self._case_objects = None
            self._case_mappings = None
            self._variants = None
            self._variant_graphs = None
            self._variant_frequency = None
            self._variants_dict = None

    def _get_log(self):
        return self._log

    def _set_log(self, log):
        self._log = log

    def _get_eog(self):
        if self._eog == None:
            self._eog = self.eog_from_log()
        return self._eog

    def _get_case_objects(self):
        if self._case_objects == None:
            self._cases, self._case_objects, self._case_mappings = self.calculate_cases()
        return self._case_objects

    def _get_cases(self):
        if self._cases == None:
            self._cases, self._case_objects, self._case_mappings = self.calculate_cases()
        return self._cases

    def _get_case_mappings(self):
        if self._cases == None:
            self._cases, self._case_objects, self._case_mappings = self.calculate_cases()
        return self._case_mappings

    def _get_variants(self):
        if self._variants == None:
            self._variants, self._variant_frequency, self._variant_graphs, self._variants_dict = self.calculate_variants()
        return self._variants

    def _get_variant_frequency(self):
        if self._variant_frequency == None:
            self._variants, self._variant_frequency, self._variant_graphs, self._variants_dict = self.calculate_variants()
        return self._variant_frequency

    def _get_variant_graphs(self):
        if self._variant_graphs == None:
            self._variants, self._variant_frequency, self._variant_graphs, self._variants_dict = self.calculate_variants()
        return self._variant_graphs

    def _get_object_types(self):
        return self._object_types

    def _set_object_types(self, object_types):
        self._object_types = object_types

    def _get_variant_timeout(self):
        return self._variant_timeout

    def _set_variant_timeout(self, variant_timeout):
        self._variant_timeout = variant_timeout

    def _get_variants_dict(self):
        if self._variants_dict == None:
            self._variants, self._variant_frequency, self._variant_graphs, self._variants_dict = self.calculate_variants()
        return self._variants_dict

    log = property(_get_log, _set_log)
    object_types = property(_get_object_types, _set_object_types)
    eog = property(_get_eog)
    cases = property(_get_cases)
    case_objects = property(_get_case_objects)
    case_mappings = property(_get_case_mappings)
    variants = property(_get_variants)
    variant_frequency = property(_get_variant_frequency)
    variant_graphs = property(_get_variant_graphs)
    variants_dict = property(_get_variants_dict)
    variant_timeout = property(_get_variant_timeout, _set_variant_timeout)

    def copy(self):
        return OCEL(self.log.copy(), object_types=self.object_types, execution_extraction=self._execution_extraction, leading_object_type=self._leading_type, variant_extraction=self._variant_extraction, variant_timeout=self.variant_timeout)
