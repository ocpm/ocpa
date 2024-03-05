import matplotlib.pyplot as plt
import matplotlib.patches as mpatches


def create_pie_chart(allowed_counts, not_allowed_counts, output_file, activity, object_type_1, object_type_2):
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
    title = f"Relative qualifier frequency for {activity} and object types {object_type_1} & {object_type_2}"
    ax.set_title(title)

    # Create custom legend handles and labels
    allowed_handles = [mpatches.Patch(color=color, label=label) for label, color in zip(allowed_counts.keys(), colors[:num_allowed])]
    not_allowed_handles = [mpatches.Patch(color=color, label=label) for label, color in zip(not_allowed_counts.keys(), colors[num_allowed:])]

    # Add the legend
    legend1 = ax.legend(handles=allowed_handles, title="Allowed Qualifiers", loc="upper left", bbox_to_anchor=(1, 1))
    ax.add_artist(legend1)
    ax.legend(handles=not_allowed_handles, title="Prohibited Qualifiers", loc="lower left", bbox_to_anchor=(1, 0))

    # Save the pie chart as a PNG file
    plt.savefig(output_file, bbox_inches='tight')
    plt.close(fig)


def check_o2o_qualifier_conformance(ocel, activity, source_type, target_type, allowed_qualifiers = []):
    G = ocel.o2o_graph.graph
    activity_events = ocel.log.log[ocel.log.log['event_activity'] == activity]

    allowed_count = {a_q:0 for a_q in allowed_qualifiers}
    not_allowed_count = {}
    not_exists_string = "No existing relationship"
    total_count = 0
    # Iterate through the activity events
    for _, event in activity_events.iterrows():
        event_id = event['event_id']
        sources = event[source_type]
        targets = event[target_type]

        for source in sources:
            for target in targets:
                # Check if there's an edge between source and target in the graph
                if G.has_edge(source, target):
                    edge_qualifier = G.edges[source, target]['qualifier']

                    # Check if the edge qualifier is in the allowed_qualifiers
                    if edge_qualifier in allowed_qualifiers:
                        allowed_count[edge_qualifier] += 1
                    else:
                        if edge_qualifier not in not_allowed_count.keys():
                            not_allowed_count[edge_qualifier] = 0
                        not_allowed_count[edge_qualifier] += 1

                # If there is no edge there is no qualifier present
                else:
                    if not_exists_string not in not_allowed_count.keys():
                        not_allowed_count[not_exists_string] = 0
                    not_allowed_count[not_exists_string] += 1

                # Increase the total count
                total_count += 1


    create_pie_chart(allowed_count, not_allowed_count, "Qualifier_Conformance.png", activity, source_type, target_type)
    return allowed_count, not_allowed_count