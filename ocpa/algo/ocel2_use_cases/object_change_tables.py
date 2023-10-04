import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.dates as mdates
import pandas as pd

def plot_attribute_over_time(ocel, object_type, target_column, group_column, filename, title=None):
    type_df = ocel.change_table.tables[object_type]
    print(type_df)
    timestamp_column = "ocel_time"
    # Sort the DataFrame by the timestamp column
    dataframe = type_df.sort_values(by=timestamp_column)

    # Set up the plot
    plt.figure(figsize=(10, 6))

    # Create a line plot using seaborn
    # dataframe[timestamp_column] = pd.to_datetime(dataframe[timestamp_column])
    sns.lineplot(data=dataframe, x=timestamp_column, y=target_column, hue=group_column, marker='o')

    # Customize the plot
    plt.xlabel('Time')
    plt.ylabel(target_column)
    if title:
        plt.title(title)

    # Format the x-axis to display only year and month
    ax = plt.gca()
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    # Rotate the x-axis labels for better readability
    plt.xticks(rotation=45)

    # Show the plot
    plt.savefig(filename, dpi = 300, bbox_inches='tight')
