
<p align="center">
  <img height="150" src="logo.jpg" />
</p>



![PyPI](https://badgen.net/badge/pypi/2.2.0/green?icon=pypi)
![Testing Status](https://badgen.net/badge/testing/passing/green?icon=github)
![Docs Status](https://badgen.net/badge/docs/passing/green?icon=)
![Contributing](https://badgen.net/badge/contributions/welcome/green?icon=github)

**[Documentation](https://pytorch-geometric.readthedocs.io)** | **[Paper](https://arxiv.org/abs/1903.02428)** | **[Colab Notebooks and Video Tutorials](https://pytorch-geometric.readthedocs.io/en/latest/get_started/colabs.html)** | 

**XFlow** is a library built upon Python to easily write and train method for a wide range of applications related to network flow problems. Tasks, datasets benchmarks, baselines and implementation are introduced below.

[comment]: <> (add icons https://css-tricks.com/adding-custom-github-badges-to-your-repo/)

--------------------------------------------------------------------------------

* [Tasks](#tasks)
* [Benchmarks](#benchmarks)
* [Implemented Baselines](#implemented-baselines)
* [Create your own models](#create-your-own-models)
* [Installation](#installation)

## Tasks

### Spreading Task 
Task, Data, and Baselines

- (max/min/understand/predict coverage, given diffusion process and starting nodes)
- important concept: ***Reverse Reachable Sets (RR set), K-core decomposition***
- IM and variants (node)
- simulation-based, proxy/heuristic based, sketch based
- Dynamic Influence Maximization, Competitive Influence Maximization
- competitive IM vs network interdiction
    - 2 or more competitors can remove/add edges or change nodes

    [](https://journals.aps.org/pre/pdf/10.1103/PhysRevE.105.044311)
    
    
### Backtracking Task
Task, Data, and Baselines

- (identify starting nodes, given diffusion process and coverage)
- If diffusion is not given
- Source Identification, or Identification of influential spreaders

### Diffusion learning

- Min-cost Max-Flow (edge), network simplex

### Explanability Task
Task, Data, and Baselines

### Multilayer

- percolation
- synchronization

Question: main-stream task of single and multilayer network has little overlap. So they can be extended to each other.

## Benchmarks

## Implemented Baselines
We list currently supported XFlow models, layers and operators according to category:

## Create your own models



### Manage experiments with GraphGym

GraphGym allows you to manage and launch GNN experiments, using a highly modularized pipeline (see [here](https://pytorch-geometric.readthedocs.io/en/latest/advanced/graphgym.html) for the accompanying tutorial).

```
git clone https://github.com/XFlow-team/pytorch_geometric.git
cd pytorch_geometric/graphgym
bash run_single.sh  # run a single GNN experiment (node/edge/graph-level)
bash run_batch.sh   # run a batch of GNN experiments, using differnt GNN designs/datasets/tasks
```

Users are highly encouraged to check out the [documentation](https://pytorch-geometric.readthedocs.io/en/latest), which contains additional tutorials on the essential functionalities of XFlow, including data handling, creation of datasets and a full list of implemented methods, transforms, and datasets.
For a quick start, check out our [examples](https://github.com/XFlow-team/pytorch_geometric/tree/master/examples) in `examples/`.


## Installation

XFlow is available for Python 3.7 to Python 3.10.

### Anaconda

You can now install XFlow via [Anaconda](https://anaconda.org/XFlow/XFlow) for all major OS/PyTorch/CUDA combinations 🤗
If you have not yet installed PyTorch, install it via `conda` as described in the [official PyTorch documentation](https://pytorch.org/get-started/locally/).
Given that you have PyTorch installed (`>=1.8.0`), simply run

```
conda install XFlow -c XFlow
```

### Pip Wheels

We alternatively provide pip wheels for all major OS/PyTorch/CUDA combinations, see [here](https://data.XFlow.org/whl).


For additional but optional functionality, run

```
pip install torch_cluster torch_spline_conv -f https://data.XFlow.org/whl/torch-1.12.0+${CUDA}.html
```


## Cite

Please cite [our paper](https://arxiv.org/abs/1903.02428) (and the respective papers of the methods used) if you use this code in your own work:

```
@inproceedings{XXX,
  title={XXX},
  author={XXX},
  booktitle={XXX},
  year={2023},
}
```

Feel free to [email us](mailto:zchen@cse.msstate.edu) if you wish your work to be listed in the [external resources](XXX).
If you notice anything unexpected, please open an [issue](XXX) and let us know.
If you have any questions or are missing a specific feature, feel free [to discuss them with us](XXX).
We are motivated to constantly make XFlow even better.




