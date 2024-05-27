import pandas as pd
import networkx as nx
import requests
from io import BytesIO, StringIO
import gzip

def eurostat_road_go_ta_tg():
    # URL of the Eurostat TSV file (compressed)
    eurostat_url = "https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/road_go_ta_tg/?format=TSV&compressed=true"

    # Download the TSV file
    response = requests.get(eurostat_url)
    data = gzip.decompress(response.content).decode('utf-8')
    data_io = StringIO(data)

    # Read the TSV file into a DataFrame with appropriate settings
    eurostat_df = pd.read_csv(data_io, delimiter='\t', on_bad_lines='skip')

    # Inspect the dataframe to understand its structure
    print(eurostat_df.head())
    print(eurostat_df.columns)

    # Split the first column into multiple columns
    metadata_columns = eurostat_df.iloc[:, 0].str.split(',', expand=True)
    metadata_columns.columns = ['freq', 'tra_type', 'nst07', 'unit', 'geo']

    # Combine metadata columns with the data columns
    eurostat_df = pd.concat([metadata_columns, eurostat_df.iloc[:, 1:]], axis=1)

    # Melt the DataFrame to have a long format
    eurostat_df = eurostat_df.melt(id_vars=['freq', 'tra_type', 'nst07', 'unit', 'geo'], 
                                   var_name='year', 
                                   value_name='value')

    # Filter out rows with missing values
    eurostat_df.dropna(subset=['value'], inplace=True)

    # Convert year to a proper format
    eurostat_df['year'] = eurostat_df['year'].str.strip()

    # Display the cleaned DataFrame
    print(eurostat_df.head())

    # Initialize a directed graph
    G = nx.DiGraph()

    # Example: Using 'geo' as origin and 'year' as destination, and 'value' as weight
    for index, row in eurostat_df.iterrows():
        origin = row['geo']
        destination = row['year']
        weight = row['value']

        # Add edge with weight
        G.add_edge(origin, destination, weight=weight)

    print(f"eurostat_road_go_ta_tg has {G.number_of_nodes()} nodes and {G.number_of_edges()} edges.")
    return G

# # Example usage
# if __name__ == "__main__":
#     G = eurostat_road_go_ta_tg()
