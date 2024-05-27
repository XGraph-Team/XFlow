import pandas as pd
import networkx as nx
import requests
from zipfile import ZipFile
from io import BytesIO

def faf5_6():
    # URL of the CSV file within the ZIP archive
    zip_url = "https://faf.ornl.gov/faf5/data/download_files/FAF5.6.zip"

    # Download the ZIP file
    response = requests.get(zip_url)
    zip_content = response.content

    # Save the ZIP file to disk (optional)
    with open("FAF5.6.zip", "wb") as zip_file:
        zip_file.write(zip_content)

    # Open the saved ZIP file
    with ZipFile("FAF5.6.zip", 'r') as zip_file:
        # Extract the relevant CSV file from the ZIP archive
        csv_file = zip_file.open("FAF5.6.csv")
        
        # Read the CSV file into a DataFrame
        faf_df = pd.read_csv(csv_file)

    # Inspect the dataframe to understand its structure
    print(faf_df.head())
    print(faf_df.columns)

    # Adjust column names based on actual data structure
    origin_col = 'dms_orig'  # Origin column
    destination_col = 'dms_dest'  # Destination column
    weight_col = 'tons_2017'  # Weight column for the year 2017 
    # TODO (adjust year as needed)

    # Initialize a directed graph
    G = nx.DiGraph()

    # Add edges to the graph from the DataFrame
    for index, row in faf_df.iterrows():
        origin = row[origin_col]
        destination = row[destination_col]
        weight = row[weight_col]

        # Add edge with weight
        G.add_edge(origin, destination, weight=weight)

    print(f"Graph has {G.number_of_nodes()} nodes and {G.number_of_edges()} edges.")
    return G

# Example usage
G = faf5_6()
