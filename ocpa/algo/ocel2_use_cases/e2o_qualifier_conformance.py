import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

def create_pie_chart(allowed_counts, not_allowed_counts, output_file, activity, attribute_lookup, object_type, qualifier):
    # Combine allowed and not_allowed counts into a single dictionary
    combined_counts = {**allowed_counts, **not_allowed_counts}

    # Sort the combined_counts dictionary by value (count) in descending order
    sorted_counts = dict(sorted(combined_counts.items(), key=lambda x: x[1], reverse=True))

    # Prepare the data for the pie chart
    labels = list(sorted_counts.keys())
    sizes = list(sorted_counts.values())
    colors = []

    # Assign shades of green for allowed values and shades of red for not allowed values
    num_allowed = len(allowed_counts)
    num_not_allowed = len(not_allowed_counts)

    for i, label in enumerate(labels):
        if label in allowed_counts:
            colors.append(plt.cm.Greens(0.5 + 0.5 * i / num_allowed))
        else:
            colors.append(plt.cm.Reds(0.5 + 0.5 * i / num_not_allowed))

    # Create the pie chart
    fig, ax = plt.subplots()
    ax.pie(sizes, colors=colors, autopct='%1.1f%%', startangle=90)

    # Equal aspect ratio ensures that pie is drawn as a circle
    ax.axis('equal')

    # Set the title
    title = f"Relative frequency of {attribute_lookup} of {object_type} which are {qualifier} for {activity} with permitted and prohibited values."
    ax.set_title(title)

    # Create custom legend handles and labels
    allowed_handles = [mpatches.Patch(color=color, label=label) for label, color in zip(allowed_counts.keys(), colors[:num_allowed])]
    not_allowed_handles = [mpatches.Patch(color=color, label=label) for label, color in zip(not_allowed_counts.keys(), colors[num_allowed:])]

    # Add the legend
    legend1 = ax.legend(handles=allowed_handles, title="Allowed Values", loc="upper left", bbox_to_anchor=(1, 1))
    ax.add_artist(legend1)
    ax.legend(handles=not_allowed_handles, title="Prohibited Values", loc="lower left", bbox_to_anchor=(1, 0))

    # Save the pie chart as a PNG file
    plt.savefig(output_file, bbox_inches='tight')
    plt.close(fig)


# Function to find the value of target_column in the last appearance of reference_value in the reference_column
def find_last_appearance_value(dataframe, target_column, reference_column, reference_value):
    last_appearance = dataframe.loc[dataframe[reference_column] == reference_value].iloc[-1]
    return last_appearance[target_column]

# Function to evaluate conformance of an event-to-object qualifier for a given activity and object type
def e2o_qualifier_conformance(ocel, activity, object_type, qualifier, permitted_attributes, attribute_lookup):
    # Initialize a dictionary for allowed attributes and their counts
    allowed_count = {pa:0 for pa in permitted_attributes}
    # Initialize a dictionary for not allowed attributes and their counts
    not_allowed_count = {}

    # Iterate through the event nodes in the event-object graph (EOG)
    for n in ocel.graph.eog.nodes:
        # Check if the current event node has the specified activity
        if ocel.get_value(n, "event_activity") == activity:
            # Get the objects of the specified object type related to the event
            obs = ocel.get_value(n, object_type)
            if obs:
                # Iterate through the related objects
                for o in obs:
                    # Check if the object is connected to the event in the EOG
                    if o in ocel.graph.eog.nodes[n].keys():
                        # Check if the qualifier between the event and the object matches the specified qualifier
                        if ocel.graph.eog.nodes[n][o] == qualifier:
                            # Find the last appearance value of the object in the change table of the object type
                            attribute_value = find_last_appearance_value(ocel.change_table.tables[object_type], attribute_lookup, "object_id", o)
                            # Update the allowed and not allowed counts based on the attribute value
                            if attribute_value in permitted_attributes:
                                allowed_count[attribute_value] += 1
                            else:
                                if not attribute_value:
                                    attribute_value = "None"
                                if attribute_value not in not_allowed_count.keys():
                                    not_allowed_count[attribute_value] = 0
                                not_allowed_count[attribute_value] += 1

    # Create a pie chart visualization of the allowed and not allowed counts
    create_pie_chart(allowed_count, not_allowed_count, "Event_Qualifier_Conformance", activity, attribute_lookup, object_type, qualifier)
    # Return the dictionaries of allowed and not allowed counts
    return allowed_count, not_allowed_count
