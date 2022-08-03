from dataclasses import dataclass
from typing import Dict

from ocpa.objects.log.variants.obj import ObjectCentricEventLog
from ocpa.objects.log.variants.graph import EventGraph
from ocpa.objects.log.variants.table import Table
from ocpa.algo.util.process_executions import factory as process_execution_factory
from ocpa.algo.util.variants import factory as variant_factory


@dataclass
class OCEL:
    log: Table
    obj: ObjectCentricEventLog
    graph: EventGraph
    parameters: Dict

    def __post_init__(self):
        self._process_executions = None
        self._process_execution_objects = None
        self._process_execution_mappings = None
        self._variants = None
        self._variant_frequency = None
        self._variant_graphs= None
        self._variants_dict = None
        self._object_types = self.log.object_types
        self._execution_extraction = self.parameters["execution_extraction"] if "execution_extraction" in self.parameters.keys() else process_execution_factory.CONN_COMP
        self._variant_calculation = self.parameters["variant_calculation"] if "variant_calculation" in self.parameters.keys() else variant_factory.TWO_PHASE
    # _get_process_execution_objects
    @property
    def process_execution_objects(self):
        if not self._process_executions:
            self._calculate_process_execution_objects()
        return self._process_execution_objects

    # _get_process_executions
    @property
    def process_executions(self):
        if not self._process_executions:
            self._calculate_process_execution_objects()
        return self._process_executions

    # _get_process_execution_mappings
    @property
    def process_execution_mappings(self):
        if not self._process_executions:
            self._calculate_process_execution_objects()
        return self._process_execution_mappings

    # _get_variants
    @property
    def variants(self):
        if not self._variants:
            self._calculate_variants()
        return self._variants


    # _get_variant_frequency
    @property
    def variant_frequencies(self):
        if not self._variant:
            self._calculate_variants()
        return self._variant_frequency

    # _get_variant_graphs
    @property
    def variant_graphs(self):
        if not self._variants:
            self._calculate_variants()
        return self._variant_graphs

    # _get_variants_dict
    @property
    def variants_dict(self):
        if not self._variants:
            self._calculate_variants()
        return self._variants_dict

    # _get_object_types
    @property
    def object_types(self):
        return self._object_types

    # _get_variants_dict
    @property
    def variants_dict(self):
        pass

    def get_value(self, e_id, attribute):
        return self.log.get_value(e_id, attribute)

    def _calculate_process_execution_objects(self):
        self._process_executions, self._process_execution_objects, self._process_execution_mappings = process_execution_factory.apply(self,self._execution_extraction,parameters=self.parameters)

    def _calculate_variants(self):
        self._variants, self._variant_frequency, self._variant_graphs, self._variants_dict = variant_factory.apply(self,self._variant_calculation,parameters=self.parameters)


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
