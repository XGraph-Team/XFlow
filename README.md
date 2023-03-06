
<p align="center">
  <img height="150" src="logo.jpg" />
</p>



![PyPI](https://badgen.net/badge/pypi/2.2.0/green?icon=pypi)
![Testing Status](https://badgen.net/badge/testing/passing/green?icon=github)
![Docs Status](https://badgen.net/badge/docs/passing/green?icon=)
![Contributing](https://badgen.net/badge/contributions/welcome/green?icon=github)

**[Documentation](https://pytorch-geometric.readthedocs.io)** | **[Paper](https://arxiv.org/abs/1903.02428)** | **[Colab Notebooks and Video Tutorials](https://pytorch-geometric.readthedocs.io/en/latest/get_started/colabs.html)** | 

**XFlow** is a library built upon Python to easily write and train method for a wide range of applications related to network flow problems. XFlow is organized task-wise, which provide datasets benchmarks, baselines and auxiliary implementation.

[comment]: <> (add icons https://css-tricks.com/adding-custom-github-badges-to-your-repo/)

--------------------------------------------------------------------------------

* [Spreading Task](#Spreading-Task)
* [Backtracking Task](#Backtracking-Task)
* [Diffusion Learning Task](#Diffusion-learning-task)
* [Explanability Task](#Explanability-Task)
* [Installation](#installation)


## Spreading Task 

[comment]: <> (put NIB here)


selected variants

- (max/min/understand/predict coverage, given diffusion process and starting nodes)
- important concept: ***Reverse Reachable Sets (RR set), K-core decomposition***
- IM and variants (node)
- simulation-based, proxy/heuristic based, sketch based
- Dynamic Influence Maximization, Competitive Influence Maximization
- competitive IM vs network interdiction
    - 2 or more competitors can remove/add edges or change nodes

    [](https://journals.aps.org/pre/pdf/10.1103/PhysRevE.105.044311)
    
### Benchmarks

### Implemented Baselines

### Create your own models
    


## Backtracking Task

selected variants

[comment]: <> (write)


- (identify starting nodes, given diffusion process and coverage)
- If diffusion is not given
- Source Identification, or Identification of influential spreaders

### Benchmarks

### Implemented Baselines

### Create your own models




## Diffusion Learning Task

selected variants

- Min-cost Max-Flow (edge), network simplex

### Benchmarks

### Implemented Baselines

### Create your own models




## Explanability Task


[comment]: <> (write)



### Benchmarks

### Implemented Baselines

### Create your own models




## Multilayer

- percolation
- synchronization

Question: main-stream task of single and multilayer network has little overlap. So they can be extended to each other.

### Benchmarks

### Implemented Baselines

### Create your own models




## Installation

XFlow is available for Python 3.7 to Python 3.10.

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

Feel free to [email us](mailto:zchen@cse.msstate.edu) if you wish your work to be listed in this repo.
If you notice anything unexpected, please open an [issue](XXX) and let us know.
If you have any questions or are missing a specific feature, feel free [to discuss them with us](XXX).
We are motivated to constantly make XFlow even better.




