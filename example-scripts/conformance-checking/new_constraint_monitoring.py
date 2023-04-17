from ocpa.objects.graph.extensive_constraint_graph.obj import ExtensiveConstraintGraph, ActivityNode, ObjectTypeNode, OAEdge, AAEdge, AOAEdge
from ocpa.objects.log.importer.ocel import factory as ocel_import_factory
from ocpa.algo.discovery.ocpn import algorithm as ocpn_discovery_factory
from ocpa.algo.enhancement.token_replay_based_performance import algorithm as performance_factory
from ocpa.objects.graph.constraint_graph.obj import ConstraintGraph, ActivityNode, ObjectTypeNode, FormulaNode, ControlFlowEdge, ObjectRelationEdge, PerformanceEdge
import ocpa.algo.conformance.constraint_monitoring.algorithm as constraint_monitoring_factory
from datetime import timedelta
from ocpa.algo.util.filtering.log import time_filtering

filename = "../../sample_logs/jsonocel/p2p-normal.jsonocel"
ocel = ocel_import_factory.apply(filename)
# ocpn = ocpn_discovery_factory.apply(ocel)

w = timedelta(weeks=4)
f_in = time_filtering.end

time_index = []
l_start = ocel.log.log["event_timestamp"].min()
l_end = ocel.log.log["event_timestamp"].max()

m = int(1 + ((l_end - l_start) / w))
sublogs = []
for i in range(0, m):
    start = l_start + i*w
    end = l_start + (i+1)*w
    time_index.append(start)
    sublog = time_filtering.extract_sublog(ocel, start, end, f_in)
    sublogs.append(sublog)



cg1 = ExtensiveConstraintGraph('Example1')
ot_application = ObjectTypeNode('PURCHREQ')
act_ca = ActivityNode('Create Purchase Requisition')
cg1.add_nodes([ot_application, act_ca])
oa1 = OAEdge(ot_application, act_ca, 'exist', '>', 0.1)
cg1.add_oa_edge(oa1)

for sublog in sublogs:
    violated, diagnostics = constraint_monitoring_factory.apply(cg1, sublog, parameters=None)
    print(violated)


# # Example1: VM and PGI should not be concurrently executed.
# cg1 = ConstraintGraph('Example1')
# act_vm = ActivityNode('Verify Material')
# act_pgi = ActivityNode('Plan Goods Issue')
# cg1.add_nodes([act_vm, act_pgi])
# cf1 = ControlFlowEdge(act_vm, act_pgi, 'concur', 'MATERIAL', 0.1)
# cg1.add_cf_edge(cf1)
# violated, diagnostics = constraint_monitoring_factory.apply(
#     cg1, ocel, diag, parameters=None)
# if violated:
#     print(diagnostics)

# # Example2: CPR should alway be followed by CPO.
# cg2 = ConstraintGraph('Example2')
# act_cpr = ActivityNode('Create Purchase Requisition (CPR)')
# act_cpo = ActivityNode('Create Purchase Order (CPO)')
# cg2.add_nodes([act_cpr, act_cpo])
# cf2 = ControlFlowEdge(act_cpr, act_cpo, 'causal', 'PURCHREQ', 0.99)
# cg2.add_cf_edge(cf2)
# violated, diagnostics = constraint_monitoring_factory.apply(
#     cg2, ocel, diag, parameters=None)
# if violated:
#     print(diagnostics)

# # Example3: CPR should not be skipped
# cg3 = ConstraintGraph('Example3')
# act_cpr = ActivityNode('Create Purchase Requisition (CPR)')
# cg3.add_nodes([act_cpr])
# cf3 = ControlFlowEdge(act_cpr, act_cpr, 'skip', 'PURCHREQ', 0)
# cg3.add_cf_edge(cf3)
# violated, diagnostics = constraint_monitoring_factory.apply(
#     cg3, ocel, diag, parameters=None)
# if violated:
#     print(diagnostics)

# # Example4: PGI should always involve PURCHORD
# cg4 = ConstraintGraph('Example4')
# act_pgi = ActivityNode('Plan Goods Issue')
# obj_node1 = ObjectTypeNode('PURCHORD')
# cg4.add_nodes([act_pgi, obj_node1])
# or1 = ObjectRelationEdge(obj_node1, act_pgi, 'absent', 0)
# cg4.add_obj_edge(or1)
# violated, diagnostics = constraint_monitoring_factory.apply(
#     cg4, ocel, diag, parameters=None)
# if violated:
#     print(diagnostics)

# # Example5: PGI should not involve MATERIAL
# cg5 = ConstraintGraph('Example5')
# act_pgi = ActivityNode('Plan Goods Issue')
# obj_node2 = ObjectTypeNode('MATERIAL')
# cg5.add_nodes([act_cpr])
# or2 = ObjectRelationEdge(obj_node2, act_pgi, 'present', 0)
# cg5.add_obj_edge(or2)
# violated, diagnostics = constraint_monitoring_factory.apply(
#     cg5, ocel, diag, parameters=None)
# if violated:
#     print(diagnostics)

# # Example6: CPO should involve only one PURCHORD
# cg6 = ConstraintGraph('Example6')
# act_cpo = ActivityNode('Create Purchase Order (CPO)')
# obj_node1 = ObjectTypeNode('PURCHORD')
# cg6.add_nodes([obj_node1, act_cpo])
# or3 = ObjectRelationEdge(obj_node1, act_cpo, 'singular', 0.99)
# cg6.add_obj_edge(or3)
# violated, diagnostics = constraint_monitoring_factory.apply(
#     cg6, ocel, diag, parameters=None)
# if violated:
#     print(diagnostics)

# # Example7: CPO should mostly involve multiple PURCHORD
# cg7 = ConstraintGraph('Example7')
# act_cpo = ActivityNode('Plan Goods Issue')
# obj_node2 = ObjectTypeNode('MATERIAL')
# cg7.add_nodes([act_cpo, obj_node2])
# or4 = ObjectRelationEdge(obj_node2, act_cpo, 'multiple', 0.7)
# cg7.add_obj_edge(or4)
# violated, diagnostics = constraint_monitoring_factory.apply(
#     cg7, ocel, diag, parameters=None)
# if violated:
#     print(diagnostics)
