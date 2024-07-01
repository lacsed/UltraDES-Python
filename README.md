<p align="center">
  <a href="https://github.com/lacsed/UltraDES">
    <img src="http://lacsed.eng.ufmg.br/wp-content/uploads/2017/05/Logo_UltraDES_PNG_Internet-e1494353854950.png" alt="AngouriMath logo" width="400">
  </a>
</p>

<h2 align="center">UltraDES Python</h2>

<p align="center">
  <b>UltraDES is a library for modeling, analysis and control of Discrete Event Systems. It has been developed at LACSED | <a href="http://www.lacsed.eng.ufmg.br">UFMG</a>.</b> 
</p>

## Before using UltraDES

Requirements: 
- Supported OS: Windows, MAC OS or Linux (Mono).

## First steps

Install using pip

### On Windows

- Install python 3.7 (we recommend anaconda distribution)
- Run 'pip install https://github.com/lacsed/UltraDES-Python/releases/download/0.0.5/ultrades_python-0.0.5-py3-none-any.whl'

### On Ubuntu

- Install [mono](https://www.mono-project.com/download/stable/#download-lin)
- Install python 3.7 or 3.8 and pip ([tutorial](https://phoenixnap.com/kb/how-to-install-python-3-ubuntu))
- Run 'sudo apt-get install clang libglib2.0-dev python3-dev'
- Run 'pip install https://github.com/lacsed/UltraDES-Python/releases/download/0.0.5/ultrades_python-0.0.5-py3-none-any.whl'


### import UltraDES

```py
import sys, ultrades, os
sys.path.append(os.path.dirname(ultrades.__file__))
from ultrades.automata import *
```

### Create States

```py
s1 = state("s1", marked = True)
s2 = state("s2", marked = False)
```

### Create Events

```py
e1 = event("e1", controllable = True)
e2 = event("e2", controllable = False)
e3 = event("e3", controllable = True)
e4 = event("e4", controllable = False)
```

### Create Automata

```py
G1 = dfa(
[
    (s1, e1, s2), 
    (s2, e2, s1)
], s1, "G1")
  
G2 = dfa(
[
    (s1, e3, s2), 
    (s2, e4, s1)
], s1, "G2")
```

## Operations with Automata

### Making a Parallel composition

```py
Gp = parallel_composition(G1, G2); 
```

### Showing the Automaton (only on Jupyter Lab)

```py
 show_automaton(Gp)
 ```
 
 ## More Functions 
 
 See the [Wiki](https://github.com/lacsed/UltraDES-Python/wiki) for more implemented functions.
 
 ## Try UltraDES-Python
 
<a href="https://colab.research.google.com/drive/1g4vS4Yppzk8nzfzyO8Kna93LkOqxXYNc?usp=sharing"><img src="https://img.shields.io/static/v1?label=Go%20to&message=Colab%20NB&color=purple&style=for-the-badge"></a>
<a href="https://colab.research.google.com/drive/1W3pWzNkyg1MMmAing3wZjBERyUJLpXN1?usp=sharing"><img src="https://img.shields.io/static/v1?label=Go%20to&message=Examples&color=pink&style=for-the-badge"></a>
