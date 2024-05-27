import os
import networkx as nx
import requests
import random
import tarfile
import ndlib.models.ModelConfig as mc

def create_folder(folder_name):
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

def download_konect_dataset(url, filename):
    response = requests.get(url)
    if response.status_code == 200:
        with open(filename, 'wb') as f:
            f.write(response.content)
    else:
        raise ValueError(f"Failed to download the dataset from {url}")

def check_and_download(url, filename):
    create_folder("konect_datasets")
    if not os.path.exists(filename):
        print(f"Downloading {filename}...")
        download_konect_dataset(url, filename)
    else:
        print(f"{filename} already exists.")

def extract_tar_bz2(filename, extract_path):
    if not os.path.exists(extract_path):
        print(f"Extracting {filename}...")
        with tarfile.open(filename, 'r:bz2') as tar:
            tar.extractall(path=extract_path)
    else:
        print(f"{extract_path} already exists.")

def add_edge_weights(G, min_weight, max_weight):
    config = mc.Configuration()
    for a, b in G.edges():
        weight = random.uniform(min_weight, max_weight)
        weight = round(weight, 2)
        config.add_edge_configuration("threshold", (a, b), weight)
        G[a][b]['weight'] = weight
    return G, config

def load_graph(filename):
    G = nx.DiGraph()
    with open(filename, 'rb') as f:
        for line in f:
            line = line.decode('utf-8', errors='ignore')
            if line.startswith('%'):
                continue  # Skip comments
            parts = line.strip().split()
            if len(parts) >= 2:
                G.add_edge(parts[0], parts[1])
    G, config = add_edge_weights(G, 0.1, 0.5)
    return G, config

def chesapeake_bay():
    url = "http://www.konect.cc/files/download.tsv.dimacs10-chesapeake.tar.bz2"
    tar_filename = "konect_datasets/dimacs10-chesapeake.tar.bz2"
    extract_path = "konect_datasets/dimacs10-chesapeake"
    check_and_download(url, tar_filename)
    extract_tar_bz2(tar_filename, extract_path)
    tsv_filename = os.path.join(extract_path, "dimacs10-chesapeake/out.dimacs10-chesapeake")
    return load_graph(tsv_filename)

def infectious():
    url = "http://www.konect.cc/files/download.tsv.infectious.tar.bz2"
    tar_filename = "konect_datasets/infectious.tar.bz2"
    extract_path = "konect_datasets/infectious"
    check_and_download(url, tar_filename)
    extract_tar_bz2(tar_filename, extract_path)
    tsv_filename = os.path.join(extract_path, "sociopatterns-infectious/out.sociopatterns-infectious")
    return load_graph(tsv_filename)


def main():
    g_chesapeake, config_chesapeake = chesapeake_bay()
    print("Chesapeake Bay: Nodes = {}, Edges = {}".format(len(g_chesapeake.nodes()), len(g_chesapeake.edges())))

    g_infectious, config_infectious = infectious()
    print("Infectious: Nodes = {}, Edges = {}".format(len(g_infectious.nodes()), len(g_infectious.edges())))

if __name__ == "__main__":
    main()
