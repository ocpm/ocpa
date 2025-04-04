"""Object-Centric Event Log"""

from dataclasses import dataclass, field
from typing import Any

import networkx as nx

from ocpa.objects.log.variants.obj import ObjectCentricEventLog
from ocpa.objects.log.variants.graph import EventGraph
from ocpa.objects.log.variants.object_graph import ObjectGraph
from ocpa.objects.log.variants.object_change_table import ObjectChangeTable
from ocpa.objects.log.variants.table import Table
from ocpa.util.constants import CONN_COMP, LEAD_TYPE, ONE_PHASE, TWO_PHASE


@dataclass
class OCEL:
    """
    Storing and processing an object-centric event log.
    -------------------
    Can be imported through the:
    1) :func:`CSV importer <ocpa.objects.log.importer.csv.factory.apply>`
    2) :func:`JSONOCEL importer <ocpa.objects.log.importer.ocel.factory.apply>`
    3) :func:`JSONXML importer <ocpa.objects.log.importer.ocel.factory.apply>`

    Properties are lazily instantiated upon calling their getter functions.
    """

    log: Table
    obj: ObjectCentricEventLog
    graph: EventGraph
    parameters: dict # =field(default_factory=dict)
    o2o_graph: ObjectGraph = None
    change_table: ObjectChangeTable = None

    def __post_init__(self) -> None:
        """
        Initializes the classes' attributes.

        Returns
        -------
        None
        """
        
        self._process_executions: list = None
        self._process_execution_objects: list = None
        self._process_execution_mappings: dict = None
        self._variants: list = None
        self._variant_frequency: list = None
        self._variant_graphs: dict = None
        self._variants_dict: dict = None
        self._object_types: list[str] = self.log.object_types
        self._execution_extraction = (
            self.parameters["execution_extraction"]
            if "execution_extraction" in self.parameters.keys()
            else CONN_COMP
        )
        self._variant_calculation = (
            self.parameters["variant_calculation"]
            if "variant_calculation" in self.parameters.keys()
            else TWO_PHASE
        )

    @property
    def process_execution_objects(self) -> list[list[tuple[str, str]]]:
        """
        Each process execution is identified by its index in the process_execution list. Using this index, one can retrieve
        this process execution's associated objects through this list.

        :return: List of the objects of an the executions. Equally indexed as the process_execution list.
        :rtype: list(list(Tuple(string, string)))
        -------

        """
        if not self._process_executions:
            self._calculate_process_execution_objects()
        return self._process_execution_objects

    # _get_process_executions
    @property
    def process_executions(self) -> list[list[int]]:
        """
        Stores the process executions (object-centric cases) of an object-centric event log. Each process execution is
        implicitly identified by its index in this list. At the corresponding index in this array, the events of the process
        execution are stored.

        Process executions are extracted through the extraction technique in the parameters dict. These are probably
        already set in the import in one of the the importers: :func:`CSV importer <ocpa.objects.log.importer.csv.factory.apply>`
        or :func:`JSONOCEL importer <ocpa.objects.log.importer.ocel.factory.apply>`
        or :func:`JSONXML importer <ocpa.objects.log.importer.ocel.factory.apply>`.
        Possible values for the parameter execution_extraction are:
            - ocpa.algo.util.process_executions.factory.CONN_COMP (:func:`function <ocpa.algo.util.process_executions.versions.connected_components>`)
            - ocpa.algo.util.process_executions.factory.LEAD_TYPE (:func:`function <ocpa.algo.util.process_executions.versions.leading_type>`)


        :return: List of process executions, where each process execution is a list of event ids
        :rtype: list(list(int))
        -------

        """
        if not self._process_executions:
            self._calculate_process_execution_objects()
        return self._process_executions

    # _get_process_execution_mappings
    @property
    def process_execution_mappings(self) -> dict:
        """
        Storing the process executions of an event.

        :return: Dictionary mapping events to the process executions that an event belong to, identified by their index in the process_execution list.
        :rtype: Dict
        -------

        """
        if not self._process_executions:
            self._calculate_process_execution_objects()
        return self._process_execution_mappings

    # _get_variants
    @property
    def variants(self) -> list[str]:
        """
        Variants are calcuated through the variant calculation technique in the parameters dict. These are probably
        already set in the import in one of the the importers: :func:`CSV importer <ocpa.objects.log.importer.csv.factory.apply>`
        or :func:`JSONOCEL importer <ocpa.objects.log.importer.ocel.factory.apply>`
        or :func:`JSONXML importer <ocpa.objects.log.importer.ocel.factory.apply>`.
        Possible values for the parameter variant_calculation are:
            - ocpa.algo.util.variants.factory.TWO_PHASE (:func:`function <ocpa.algo.util.variants.versions.twophase>`)
            - ocpa.algo.util.variants.factory.ONE_PHASE (:func:`function <ocpa.algo.util.variants.versions.onephase>`)


        :return: List of variants identified by a unique string
        :rtype: list(str)
        -------

        """
        if not self._variants:
            self._calculate_variants()
        return self._variants

    # _get_variant_frequency
    @property
    def variant_frequencies(self) -> list[float]:
        """
        Each variant is identified by its index in the variants list. Using this index, one can retrieve
        this variants's frequency through this list.

        :return: List of the frequencies of the variants. Equally indexed as the variants list.
        :rtype: list(float)
        -------

        """
        if not self._variants:
            self._calculate_variants()
        return self._variant_frequency

    # _get_variant_graphs
    @property
    def variant_graphs(self) -> dict:
        """
        Stores the graph of a variant.

        :return: Dict mapping a variant identifier to this variant's graph labeled with activity and object types
        :rtype: Tuple(nx.DiGraph, list(Tuple(string, string)))
        -------

        """
        if not self._variants:
            self._calculate_variants()
        return self._variant_graphs

    # _get_variants_dict
    @property
    def variants_dict(self) -> dict:
        """
        Stores the process_executions associated with a variant.

        :return: Dict mapping a variant identifier to this variant's process executions (as indexes of the process_execution list)
        :rtype: Dict
        -------

        """
        if not self._variants:
            self._calculate_variants()
        return self._variants_dict

    # _get_object_types
    @property
    def object_types(self) -> list[str]:
        """
        Stores the object types of the event log.

        Set through the parameters in the import.

        :return: list of object types
        :rtype: list(str)
        -------

        """
        return self._object_types

    def get_value(self, e_id: int, attribute: str) -> Any:
        """Returns the attribute value of an event efficiently.

        The event id (e_id) refers to the event_id attribute of an event, not the index of the event in the dataframe.
        This function is the most efficient attribute value retrieval available.

        :param e_id: event id of the targeted event
        :type e_id: int
        :param attribute: attribute name of the targeted attribute, should be a column of the initial dataframe (check event_ prefix)
        :type attribute: string
        :return: any value
        :rtype: anytype
        """
        return self.log.get_value(e_id, attribute)

    def get_object_attribute_value(self, o_id: str, attribute: str):
        """Returns the attribute value of an object attribute if the attribute table was provided.

        The object id o_id refers to the object_id attribute of an object in the corresponding table that was passed.
        This function is the most efficient attribute value retrieval.

        :param o_id: object id of the targeted object
        :type o_id: str
        :param attribute: attribute name of the targeted attribute, should be a column of the passed table
        :type attribute: string
        :return: any value
        :rtype: anytype
        """
        return self.log.get_object_attribute_value(o_id, attribute)

    def get_process_execution_graph(self, process_exec_id: int) -> nx.Graph:
        """Returns the process execution graph of a process execution.

        The process_exec_id refers to the index of the process execution in the list of process executions held by this
        class.

        :param process_exec_id: index of the targeted process execution
        :type process_exec_id: int
        :return: process execution graph
        :rtype: NetworkX Graph
        """
        return self.graph.eog.subgraph(self.process_executions[process_exec_id])

    
    def _calculate_process_execution_objects(self):
        from ocpa.algo.util.process_executions import (
            factory as process_execution_factory,
        )

        (
            self._process_executions,
            self._process_execution_objects,
            self._process_execution_mappings,
        ) = process_execution_factory.apply(
            self, self._execution_extraction, parameters=self.parameters
        )

    def _calculate_variants(self):
        from ocpa.algo.util.variants import factory as variant_factory

        (
            self._variants,
            self._variant_frequency,
            self._variant_graphs,
            self._variants_dict,
        ) = variant_factory.apply(
            self, self._variant_calculation, parameters=self.parameters
        )
