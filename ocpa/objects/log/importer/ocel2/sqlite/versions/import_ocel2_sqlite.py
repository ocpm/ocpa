from ocpa.objects.log.ocel import OCEL
from typing import Dict, List, Any, Union
import sqlite3
import pandas as pd
from ocpa.objects.log.variants.table import Table
from ocpa.objects.log.variants.graph import EventGraph
from ocpa.objects.log.variants.object_graph import ObjectGraph
from ocpa.objects.log.variants.object_change_table import ObjectChangeTable
import ocpa.objects.log.variants.util.table as table_utils
import ocpa.objects.log.converter.versions.df_to_ocel as obj_converter
import networkx as nx
pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)

def apply(filepath, parameters: Dict = {}) -> OCEL:
    # Connect to the SQLite database
    # An example of reading all of the table
    # connection = sqlite3.connect(filepath)
    # cursor = connection.cursor()
    #
    # # Define the fixed tables in the database
    # fixed_tables = ['event', 'event_map_type', 'object', 'event_object', 'object_map_type']
    #
    # # Query and print the content of each fixed table
    # for table in fixed_tables:
    #     print(f"Content of table '{table}':")
    #     cursor.execute(f'SELECT * FROM {table}')
    #     rows = cursor.fetchall()
    #     for row in rows:
    #         print(row)
    #     print()
    #
    # # Query the event_map_type table to get the dynamic event tables
    # cursor.execute('SELECT ocel_type_map FROM event_map_type')
    # event_types = cursor.fetchall()
    #
    # # Query and print the content of each dynamic event table
    # for event_type in event_types:
    #     table_name = f"event_{event_type[0]}"
    #     print(f"Content of table '{table_name}':")
    #     cursor.execute(f'SELECT * FROM {table_name}')
    #     rows = cursor.fetchall()
    #     for row in rows:
    #         print(row)
    #     print()
    #
    # # Query the object_map_type table to get the dynamic object tables
    # cursor.execute('SELECT ocel_type_map FROM object_map_type')
    # object_types = cursor.fetchall()
    #
    # # Query and print the content of each dynamic object table
    # for object_type in object_types:
    #     table_name = f"object_{object_type[0]}"
    #     print(f"Content of table '{table_name}':")
    #     cursor.execute(f'SELECT * FROM {table_name}')
    #     rows = cursor.fetchall()
    #     for row in rows:
    #         print(row)
    #     print()
    #
    # # Close the connection to the database
    # connection.close()



    ######## Creating the log object as a dataframe
    # Connect to the SQLite database
    connection = sqlite3.connect(filepath)

    # Read the event table into a DataFrame
    event_df = pd.read_sql('SELECT ocel_id as event_id, ocel_type as event_activity FROM event', connection)

    # Read the event_map_type table to get the dynamic event tables
    event_types = pd.read_sql('SELECT ocel_type_map FROM event_map_type', connection)

    # Read each dynamically generated event_[ocel_type_map] table, create a DataFrame and store them in a list
    for event_type in event_types['ocel_type_map']:
        table_name = f"event_{event_type}"
        event_type_df = pd.read_sql(f'SELECT * FROM {table_name}', connection)

        # Rename the columns to avoid conflicts while merging and add the 'event_' prefix
        event_type_df.rename(columns=lambda col: f'event_{col}' if col != 'ocel_id' else 'event_id', inplace=True)
        event_type_df.rename(columns={'event_ocel_time': f'event_timestamp_{event_type}'}, inplace=True)

        # Merge the event_df with the event_type_df
        event_df = event_df.merge(event_type_df, on='event_id', how='left')

    # Combine all event_timestamp columns into one
    event_df['event_timestamp'] = event_df.filter(like='event_timestamp_').bfill(axis=1).iloc[:, 0]
    event_df.drop(event_df.filter(like='event_timestamp_').columns, axis=1, inplace=True)

    # Read the unique ocel_type values from the object table
    object_types = pd.read_sql('SELECT DISTINCT ocel_type FROM object', connection)

    # Initialize the additional columns with empty sets
    for object_type in object_types['ocel_type']:
        event_df[object_type] = event_df['event_id'].apply(lambda x: set())

    # Read the event_object table and populate the sets for each event_id
    event_object_df = pd.read_sql('SELECT ocel_event_id, ocel_object_id, ocel_qualifier FROM event_object', connection)
    object_df = pd.read_sql('SELECT ocel_id as object_id, ocel_type FROM object', connection)

    # Merge event_object_df with object_df to get the ocel_type for each ocel_object_id
    event_object_merged = event_object_df.merge(object_df, left_on='ocel_object_id', right_on='object_id')
    event_object_merged = event_object_merged[['ocel_event_id', 'ocel_object_id', 'ocel_type']]

    # Add the objects for each event and each object type
    # Collect the objects of each type for each event
    aggregated_data = event_object_merged.groupby(['ocel_event_id', 'ocel_type'])['ocel_object_id'].apply(set).unstack(
        fill_value=set())

    # Merge this aggregated data into event_df for each object type
    for object_type in aggregated_data.columns:

        # Update the event_df with the aggregated sets for each object type, merging on index event_it
        event_df.update(aggregated_data[object_type])

    # Close the connection to the database
    connection.close()

    # Set the table_df variable
    #event_df["event_id"] = list(range(0,len(event_df)))
    #print(event_df)
    event_df['event_timestamp'] = pd.to_datetime(event_df['event_timestamp'])
    if "obj_names" not in parameters:
        parameters["obj_names"] = [c for c in event_df.columns if not c.startswith("event_")]

    log = Table(event_df, parameters=parameters)
    obj = obj_converter.apply(event_df)
    graph = EventGraph(table_utils.eog_from_log(log,qualifiers=qualifiers_from_file(filepath)))
    o2o_graph = ObjectGraph(o2o_graph_from_file(filepath))
    change_table = ObjectChangeTable(change_tables_from_file(filepath))
    ocel = OCEL(log, obj, graph, parameters, o2o_graph, change_table)
    return ocel


def o2o_graph_from_file(filepath):
    # Connect to the SQLite database
    connection = sqlite3.connect(filepath)

    # Read the objects table into a DataFrame
    objects_df = pd.read_sql('SELECT ocel_id as object_id FROM object', connection)

    # Read the object_object table into a DataFrame
    object_object_df = pd.read_sql('SELECT ocel_source_id, ocel_target_id, ocel_qualifier FROM object_object',
                                   connection)

    # Close the connection to the database
    connection.close()

    # Create a directed graph
    G = nx.DiGraph()

    # Add nodes to the graph
    for object_id in objects_df['object_id']:
        G.add_node(object_id)

    # Add edges to the graph with the qualifier as an attribute
    for index, row in object_object_df.iterrows():
        G.add_edge(row['ocel_source_id'], row['ocel_target_id'], qualifier=row['ocel_qualifier'])
    return G


def change_tables_from_file(filepath):
    # Connect to the SQLite database
    connection = sqlite3.connect(filepath)

    # Read the unique ocel_type values from the object table
    object_types = pd.read_sql('SELECT DISTINCT ocel_type FROM object', connection)

    # Read the object_map_type table to get the dynamic object tables
    object_map_types = pd.read_sql('SELECT ocel_type, ocel_type_map FROM object_map_type', connection)

    # Initialize the dictionary to store the mappings
    object_type_dataframes = {}

    # Iterate through the object types and read the corresponding object_[ocel_type_map] table
    for object_type in object_types['ocel_type']:
        ocel_type_map = object_map_types.loc[object_map_types['ocel_type'] == object_type, 'ocel_type_map'].values[0]
        table_name = f"object_{ocel_type_map}"
        object_type_df = pd.read_sql(f'SELECT * FROM {table_name}', connection)
        object_type_df.rename(columns={'ocel_id': 'object_id'}, inplace=True)

        # Add the DataFrame to the dictionary
        object_type_dataframes[object_type] = object_type_df

    # Close the connection to the database
    connection.close()
    return object_type_dataframes


def qualifiers_from_file(filepath):
    # Connect to the SQLite database
    connection = sqlite3.connect(filepath)

    # Read the event_object table into a DataFrame
    event_object_df = pd.read_sql('SELECT ocel_event_id, ocel_object_id, ocel_qualifier FROM event_object', connection)

    # Close the connection to the database
    connection.close()

    # Initialize the dictionary to store the mappings
    event_id_object_mappings = {}

    # Iterate through the rows in the event_object_df and populate the dictionaries
    for index, row in event_object_df.iterrows():
        event_id = row['ocel_event_id']
        object_id = row['ocel_object_id']
        qualifier = row['ocel_qualifier']

        # If the event_id is not in the dictionary, initialize an empty dictionary for it
        if event_id not in event_id_object_mappings:
            event_id_object_mappings[event_id] = {}

        # Add the object_id and qualifier to the dictionary for the current event_id
        event_id_object_mappings[event_id][object_id] = qualifier
    return event_id_object_mappings
