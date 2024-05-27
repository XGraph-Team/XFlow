import os
import networkx as nx
import requests
import random
import ndlib.models.ModelConfig as mc
import gzip

def create_folder(folder_name):
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

def download_snap_dataset(url, filename):
    response = requests.get(url)
    with open(filename, 'wb') as f:
        f.write(response.content)

def check_and_download(url, filename):
    create_folder("snap_datasets")  # Ensure the folder is created
    if not os.path.exists(filename):
        print(f"Downloading {filename}...")
        download_snap_dataset(url, filename)
    try:
        with gzip.open(filename, 'rt') as f:
            f.read(1)
    except (OSError, gzip.BadGzipFile):
        print(f"{filename} is corrupted. Re-downloading...")
        download_snap_dataset(url, filename)

def add_edge_weights(G, min_weight, max_weight):
    config = mc.Configuration()
    for a, b in G.edges():
        weight = random.uniform(min_weight, max_weight)
        weight = round(weight, 2)
        config.add_edge_configuration("threshold", (a, b), weight)
        G[a][b]['weight'] = weight
    return G, config

def load_graph(filename):
    G = nx.read_edgelist(filename)
    G, config = add_edge_weights(G, 0.1, 0.5)
    return G, config

def soc_epinions1():
    url = "https://snap.stanford.edu/data/soc-Epinions1.txt.gz"
    filename = "snap_datasets/soc-Epinions1.txt.gz"
    check_and_download(url, filename)
    return load_graph(filename)

def soc_livejournal1():
    url = "https://snap.stanford.edu/data/soc-LiveJournal1.txt.gz"
    filename = "snap_datasets/soc-LiveJournal1.txt.gz"
    check_and_download(url, filename)
    return load_graph(filename)

def wiki_vote():
    url = "https://snap.stanford.edu/data/wiki-Vote.txt.gz"
    filename = "snap_datasets/wiki-Vote.txt.gz"
    check_and_download(url, filename)
    return load_graph(filename)

def email_euall():
    url = "https://snap.stanford.edu/data/email-EuAll.txt.gz"
    filename = "snap_datasets/email-EuAll.txt.gz"
    check_and_download(url, filename)
    return load_graph(filename)

def email_enron():
    url = "https://snap.stanford.edu/data/email-Enron.txt.gz"
    filename = "snap_datasets/email-Enron.txt.gz"
    check_and_download(url, filename)
    return load_graph(filename)

def wiki_talk():
    url = "https://snap.stanford.edu/data/wiki-Talk.txt.gz"
    filename = "snap_datasets/wiki-Talk.txt.gz"
    check_and_download(url, filename)
    return load_graph(filename)

def cit_hepph():
    url = "https://snap.stanford.edu/data/cit-HepPh.txt.gz"
    filename = "snap_datasets/cit-HepPh.txt.gz"
    check_and_download(url, filename)
    return load_graph(filename)

def cit_hepth():
    url = "https://snap.stanford.edu/data/cit-HepTh.txt.gz"
    filename = "snap_datasets/cit-HepTh.txt.gz"
    check_and_download(url, filename)
    return load_graph(filename)

def cit_patents():
    url = "https://snap.stanford.edu/data/cit-Patents.txt.gz"
    filename = "snap_datasets/cit-Patents.txt.gz"
    check_and_download(url, filename)
    return load_graph(filename)

def preprocess_stackoverflow(filename):
    with gzip.open(filename, 'rt') as f:
        lines = f.readlines()
    
    with open("snap_datasets/stackoverflow_preprocessed.txt", 'w') as f:
        for line in lines:
            parts = line.split()
            if len(parts) == 3:
                src, dst, timestamp = parts
                f.write(f"{src} {dst}\n")
            else:
                f.write(line)

def sx_stackoverflow():
    url = "https://snap.stanford.edu/data/sx-stackoverflow.txt.gz"
    filename = "snap_datasets/sx-stackoverflow.txt.gz"
    check_and_download(url, filename)
    preprocess_stackoverflow(filename)
    return load_graph("snap_datasets/stackoverflow_preprocessed.txt")

def preprocess_temporal(filename, output_filename):
    with gzip.open(filename, 'rt') as f:
        lines = f.readlines()
    
    with open(output_filename, 'w') as f:
        for line in lines:
            parts = line.split()
            if len(parts) >= 2:
                src, dst = parts[:2]
                f.write(f"{src} {dst}\n")
            else:
                f.write(line)

def sx_mathoverflow():
    url = "https://snap.stanford.edu/data/sx-mathoverflow.txt.gz"
    filename = "snap_datasets/sx-mathoverflow.txt.gz"
    check_and_download(url, filename)
    preprocess_temporal(filename, "snap_datasets/mathoverflow_preprocessed.txt")
    return load_graph("snap_datasets/mathoverflow_preprocessed.txt")

def sx_superuser():
    url = "https://snap.stanford.edu/data/sx-superuser.txt.gz"
    filename = "snap_datasets/sx-superuser.txt.gz"
    check_and_download(url, filename)
    preprocess_temporal(filename, "snap_datasets/superuser_preprocessed.txt")
    return load_graph("snap_datasets/superuser_preprocessed.txt")

def sx_askubuntu():
    url = "https://snap.stanford.edu/data/sx-askubuntu.txt.gz"
    filename = "snap_datasets/sx-askubuntu.txt.gz"
    check_and_download(url, filename)
    preprocess_temporal(filename, "snap_datasets/askubuntu_preprocessed.txt")
    return load_graph("snap_datasets/askubuntu_preprocessed.txt")

def wiki_talk_temporal():
    url = "https://snap.stanford.edu/data/wiki-talk-temporal.txt.gz"
    filename = "snap_datasets/wiki-talk-temporal.txt.gz"
    check_and_download(url, filename)
    preprocess_temporal(filename, "snap_datasets/wiki_talk_temporal_preprocessed.txt")
    return load_graph("snap_datasets/wiki_talk_temporal_preprocessed.txt")

def email_eu_core_temporal():
    url = "https://snap.stanford.edu/data/email-Eu-core-temporal.txt.gz"
    filename = "snap_datasets/email-Eu-core-temporal.txt.gz"
    check_and_download(url, filename)
    preprocess_temporal(filename, "snap_datasets/email_eu_core_temporal_preprocessed.txt")
    return load_graph("snap_datasets/email_eu_core_temporal_preprocessed.txt")

def college_msg():
    url = "https://snap.stanford.edu/data/CollegeMsg.txt.gz"
    filename = "snap_datasets/CollegeMsg.txt.gz"
    check_and_download(url, filename)
    preprocess_temporal(filename, "snap_datasets/CollegeMsg_preprocessed.txt")
    return load_graph("snap_datasets/CollegeMsg_preprocessed.txt")

def main():

    g_epinions, config_epinions = soc_epinions1()
    print("Epinions: Nodes = {}, Edges = {}".format(len(g_epinions.nodes()), len(g_epinions.edges())))

    g_livejournal, config_livejournal = soc_livejournal1()
    print("LiveJournal: Nodes = {}, Edges = {}".format(len(g_livejournal.nodes()), len(g_livejournal.edges())))

    g_wiki_vote, config_wiki_vote = wiki_vote()
    print("Wiki Vote: Nodes = {}, Edges = {}".format(len(g_wiki_vote.nodes()), len(g_wiki_vote.edges())))

    g_email_euall, config_email_euall = email_euall()
    print("Email EU All: Nodes = {}, Edges = {}".format(len(g_email_euall.nodes()), len(g_email_euall.edges())))

    g_email_enron, config_email_enron = email_enron()
    print("Email Enron: Nodes = {}, Edges = {}".format(len(g_email_enron.nodes()), len(g_email_enron.edges())))

    g_wiki_talk, config_wiki_talk = wiki_talk()
    print("Wiki Talk: Nodes = {}, Edges = {}".format(len(g_wiki_talk.nodes()), len(g_wiki_talk.edges())))

    g_cit_hepph, config_cit_hepph = cit_hepph()
    print("Citations HepPh: Nodes = {}, Edges = {}".format(len(g_cit_hepph.nodes()), len(g_cit_hepph.edges())))

    g_cit_hepth, config_cit_hepth = cit_hepth()
    print("Citations HepTh: Nodes = {}, Edges = {}".format(len(g_cit_hepth.nodes()), len(g_cit_hepth.edges())))

    g_cit_patents, config_cit_patents = cit_patents()
    print("Citations Patents: Nodes = {}, Edges = {}".format(len(g_cit_patents.nodes()), len(g_cit_patents.edges())))

    g_stackoverflow, config_stackoverflow = sx_stackoverflow()
    print("Stack Overflow: Nodes = {}, Edges = {}".format(len(g_stackoverflow.nodes()), len(g_stackoverflow.edges())))

    g_mathoverflow, config_mathoverflow = sx_mathoverflow()
    print("Math Overflow: Nodes = {}, Edges = {}".format(len(g_mathoverflow.nodes()), len(g_mathoverflow.edges())))

    g_superuser, config_superuser = sx_superuser()
    print("Super User: Nodes = {}, Edges = {}".format(len(g_superuser.nodes()), len(g_superuser.edges())))

    g_askubuntu, config_askubuntu = sx_askubuntu()
    print("Ask Ubuntu: Nodes = {}, Edges = {}".format(len(g_askubuntu.nodes()), len(g_askubuntu.edges())))

    g_wiki_talk_temporal, config_wiki_talk_temporal = wiki_talk_temporal()
    print("Wiki Talk Temporal: Nodes = {}, Edges = {}".format(len(g_wiki_talk_temporal.nodes()), len(g_wiki_talk_temporal.edges())))

    g_email_eu_core_temporal, config_email_eu_core_temporal = email_eu_core_temporal()
    print("Email EU Core Temporal: Nodes = {}, Edges = {}".format(len(g_email_eu_core_temporal.nodes()), len(g_email_eu_core_temporal.edges())))

    g_college_msg, config_college_msg = college_msg()
    print("College Msg: Nodes = {}, Edges = {}".format(len(g_college_msg.nodes()), len(g_college_msg.edges())))

if __name__ == "__main__":
    main()
