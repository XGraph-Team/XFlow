
<p align="center">
  <img height="100" src="logo.png" />
</p>



![PyPI](https://badgen.net/badge/pypi/0.0.0/green?icon=pypi)
![Testing Status](https://badgen.net/badge/testing/passing/green?icon=github)
![Docs Status](https://badgen.net/badge/docs/passing/green?icon=)
![Contributing](https://badgen.net/badge/contributions/welcome/green?icon=github)

**[XFlow Homepage](https://xflow.network)** | **[Documentation](https://xflow.network/docs)** | **[Paper Collection](https://xflow.network)** | **[Colab Notebooks Tutorials](https://xflow.network)** 

**XFlow** is a library built upon Python to easily write and train method for a wide range of applications related to network flow problems. XFlow is organized task-wise, which provide datasets benchmarks, baselines and auxiliary implementation.

[comment]: <> (add icons https://css-tricks.com/adding-custom-github-badges-to-your-repo/)




# Installation

```
pip install xflow-net
```

# Example

```python
from xflow.dataset import cora, random, ba
from xflow.diffusion import ic, si
from xflow.seed import random, degree, eigen
from xflow.method.im import celf, sigma

# graphs to test
gs = [cora, random, ba]

# diffusion models to test
df = [ic, si]

# seed configurations to test
se = [random, degree, eigen]

# methods to test
me = [celf, sigma, imrank]

# configurations of experiments
rt = run(graph=gs, diffusion=df, seed=se, method=me, eval='im', epoch=10, output=['animation', 'csv', 'fig'])
```

[Result]

# Create your own models



# Benchmark Task

## Influence Maximization
- simulation: [greedy](https://dl.acm.org/doi/10.1145/956750.956769), [CELF](https://dl.acm.org/doi/abs/10.1145/1281192.1281239), and [CELF++](https://dl.acm.org/doi/10.1145/1963192.1963217), 
- proxy: [pi](https://ojs.aaai.org/index.php/AAAI/article/view/21694), [sigma](https://ieeexplore.ieee.org/document/8661648), degree, and [eigen-centrality](https://en.wikipedia.org/wiki/Eigenvector_centrality)
- sketch: [RIS](https://epubs.siam.org/doi/abs/10.1137/1.9781611973402.70), [SKIM](https://dl.acm.org/doi/10.1145/2661829.2662077), [IMM](https://dl.acm.org/doi/10.1145/2723372.2723734) 
       
## Blocking Maximization
- [greedy](https://dl.acm.org/doi/10.1145/956750.956769)
- [pi](https://ojs.aaai.org/index.php/AAAI/article/view/21694)
- [sigma](https://ieeexplore.ieee.org/document/8661648)
- [eigen-centrality](https://en.wikipedia.org/wiki/Eigenvector_centrality)
- degree
  
## Source Localization
- [NETSLEUTH](https://ieeexplore.ieee.org/document/6413787) (Legacy and Fast versions)
- [Jordan Centrality](https://ieeexplore.ieee.org/stamp/stamp.jsp?arnumber=7913632)
- [LISN](https://ieeexplore.ieee.org/stamp/stamp.jsp?arnumber=8697898).

## Experimental Configurations
- Graphs: Compatiable with graph objects/class by [Networkx](https://networkx.org/) and [Pytorch Geometric](https://pytorch-geometric.readthedocs.io/en/latest/)
- Diffusion Models: Support [NDLib](https://ndlib.readthedocs.io/en/latest/)

# Contact
Feel free to [email us](mailto:zchen@cse.msstate.edu) if you wish your work to be listed in this repo.
If you notice anything unexpected, please open an [issue](XXX) and let us know.
If you have any questions or are missing a specific feature, feel free [to discuss them with us](XXX).
We are motivated to constantly make XFlow even better.




