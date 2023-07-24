import csv
from ocpa.objects.aopm.action_engine.obj import ConstraintInstance

def apply(file_path):
    constraint_instances = []
    with open(file_path, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            name = row['name']
            start_timestamp = int(row['start_timestamp'])
            end_timestamp = int(row['end_timestamp'])
            constraint_instance = ConstraintInstance(name, start_timestamp, end_timestamp)
            constraint_instances.append(constraint_instance)
    return constraint_instances
