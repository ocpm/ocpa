from ocpa.objects.log.importer.ocel2.sqlite import factory as ocel_import_factory
import matplotlib.pyplot as plt
import seaborn as sns
from collections import defaultdict
from ocpa.algo.predictive_monitoring import factory as predictive_monitoring
from ocpa.algo.predictive_monitoring import tabular
from ocpa.objects.log.exporter.ocel import factory as ocel_export_factory
ocel = ocel_import_factory.apply("../../sample_logs/ocel2/sqlite/<your log name>.sqlite")
#This log can be imported into OCpi (www.ocpi.ai) to discover a Petri net and its variants
ocel_export_factory.apply(ocel, './output/<your log name>.jsonocel')

#Basic log statistics
print("Number of Events: "+str(len(ocel.log.log)))
print("Number of Process Executions: "+str(len(ocel.process_executions)))
print("Number of Variants: "+ str(len(ocel.variants)))
print("Number of Activities: "+ str(len(ocel.log.log["event_activity"].unique())))

#Variant Distribution
frequencies = ocel.variant_frequencies
values = range(len(frequencies))
plt.bar(values, frequencies)
plt.xlabel('Variant')
plt.ylabel('Frequency')
plt.title('Frequency Distribution')
plt.savefig("output/variant_distribution.png", dpi = 300)

#Pexec length distribution
length_frequencies = defaultdict(int)  # default value of int is 0
for pexec in ocel.process_executions:
    length_frequencies[len(pexec)] += 1
length_frequencies = dict(length_frequencies)
(length,frequency) = zip(*length_frequencies.items())
plt.bar(length, frequency)
plt.xlabel('Process Execution Length')
plt.ylabel('Frequency')
plt.title('Frequency Distribution')
plt.savefig("output/pexec_length_distribution.png", dpi = 300)

#Calculate some more advanced featuers
activities = list(set(ocel.log.log["event_activity"].tolist()))
feature_set = [(predictive_monitoring.EVENT_SYNCHRONIZATION_TIME, ()),
               (predictive_monitoring.EVENT_POOLING_TIME, ("Container",))]  + [(predictive_monitoring.EVENT_ACTIVITY, (act,))
     for act in activities]
feature_storage = predictive_monitoring.apply(ocel, feature_set, [])
table = tabular.construct_table(
    feature_storage)
for act in activities:
    filtered_table = table[table[(predictive_monitoring.EVENT_ACTIVITY, (act,))]==1]
    print("_________")
    print("For activity "+act+":")
    print("Average Synchronization time: "+str(filtered_table[(predictive_monitoring.EVENT_SYNCHRONIZATION_TIME, ())].mean()))
    print("Average Pooling time for container: " + str(
        filtered_table[(predictive_monitoring.EVENT_POOLING_TIME, ("Container",))].mean()))
    print("_________")