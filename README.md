
<p align="center">
  <img height="100" src="logo.png" />
</p>



![PyPI](https://badgen.net/badge/pypi/0.0.10/green?icon=pypi)
![Testing Status](https://badgen.net/badge/testing/passing/green?icon=github)
![Docs Status](https://badgen.net/badge/docs/passing/green?icon=)
![Contributing](https://badgen.net/badge/contributions/welcome/green?icon=github)

**[XFlow Homepage](https://xflow.network)** | **[XFlow Paper](https://arxiv.org/abs/2308.03819)** | **[Documentation](https://xflow.network/docs)** | **[Paper Collection](https://github.com/aquastar/awesome-network-flow)** 

**XFlow** is a library built upon Python to easily write and train method for a wide range of applications related to graph flow problems. XFlow is organized task-wise, which provide datasets benchmarks, baselines and auxiliary implementation.

**Update**: [FlowGPT](https://chat.openai.com/g/g-2jt5LFYXE-flowgpt): a custom GPT for graph dynamics analysis.

[comment]: <> (add icons https://css-tricks.com/adding-custom-github-badges-to-your-repo/)



# Installation

```
pip install xflow-net
```

# Example

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/1N0gFLSOl1r4h0tvqzStssEZSnmNMvoHc?usp=sharing&pli=1#scrollTo=iXN5BYm4sh4T)

```python
import xflow

from xflow.dataset.nx import BA, connSW
from xflow.dataset.pyg import Cora
from xflow.diffusion import SI, IC, LT
from xflow.util import run

# graphs to test
fn = lambda: connSW(n=1000, beta=0.1)
fn.__name__ = 'connSW'
gs = [Cora, fn, BA]

# Diffusion models to test
df = [SI, IC, LT]

# Configurations of IM experiments
from xflow.method.im import pi as im_pi, degree as im_degree, sigma as im_sigma, celfpp as im_celfpp, greedy as im_greedy
me = [im_pi]
rt = run (
    graph = gs, diffusion = df,
    method = me, eval = 'im', epoch = 10, 
    budget = 10, 
    output = [ 'animation', 'csv', 'fig'])
```


See more examples in folder `examples`



# Benchmark Task

## Influence Maximization
- simulation: [greedy](https://dl.acm.org/doi/10.1145/956750.956769), [CELF](https://dl.acm.org/doi/abs/10.1145/1281192.1281239), and [CELF++](https://dl.acm.org/doi/10.1145/1963192.1963217), 
- proxy: [pi](https://ojs.aaai.org/index.php/AAAI/article/view/21694), [sigma](https://ieeexplore.ieee.org/document/8661648), degree, and [eigen-centrality](https://en.wikipedia.org/wiki/Eigenvector_centrality)
- sketch: [RIS](https://epubs.siam.org/doi/abs/10.1137/1.9781611973402.70)
<!-- - , [SKIM](https://dl.acm.org/doi/10.1145/2661829.2662077), [IMM](https://dl.acm.org/doi/10.1145/2723372.2723734)  -->
       
## Blocking Maximization
- [greedy](https://dl.acm.org/doi/10.1145/956750.956769)
- [pi](https://ojs.aaai.org/index.php/AAAI/article/view/21694)
- [sigma](https://ieeexplore.ieee.org/document/8661648)
- [eigen-centrality](https://en.wikipedia.org/wiki/Eigenvector_centrality)
- degree
  
## Source Localization
- [NETSLEUTH](https://ieeexplore.ieee.org/document/6413787) (Legacy and Fast versions)
- [Jordan Centrality](https://ieeexplore.ieee.org/stamp/stamp.jsp?arnumber=7913632)
- [LISN](https://ieeexplore.ieee.org/stamp/stamp.jsp?arnumber=8697898)

## Experimental Configurations
- Graphs: Compatible with graph objects/class by [Networkx](https://networkx.org/) and [Pytorch Geometric](https://pytorch-geometric.readthedocs.io/en/latest/)
- Diffusion Models: Support [NDLib](https://ndlib.readthedocs.io/en/latest/)

## How to Cite
We acknowledge the importance of good software to support research, and we note
that research becomes more valuable when it is communicated effectively. To
To demonstrate the value of XFlow, we ask that you cite XFlow in your work.

```latex
@article{zhang2023xflow,
  title={XFlow: Benchmarking Flow Behaviors over Graphs},
  author={Zhang, Zijian and Zhang, Zonghan and Chen, Zhiqian},
  journal={arXiv preprint arXiv:2308.03819},
  year={2023}
}
```

# Contact
Feel free to [email us](mailto:zchen@cse.msstate.edu) if you wish your work to be listed in this repo.
If you notice anything unexpected, please open an [issue](XXX) and let us know.
If you have any questions or are missing a specific feature, feel free [to discuss them with us](XXX).
We are motivated to constantly make XFlow even better.




