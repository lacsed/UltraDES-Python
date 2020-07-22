# UltraDES Python

UltraDES is a library for modeling, analysis and control of Discrete Event Systems. It has been developed at LACSED | UFMG (http://www.lacsed.eng.ufmg.br).

![UltraDES](http://lacsed.eng.ufmg.br/wp-content/uploads/2017/05/Logo_UltraDES_PNG_Internet-e1494353854950.png)

## Before using UltraDES

Requirements: 
- Supported OS: Windows, MAC OS or Linux (Mono).

## First steps

Install using pip

### Import UltraDES

```py
from ultrades.automata import *
```

### Creating States

```py
s1 = state("s1", marked = True)
s2 = state("s2", marked = False)
```

### Creating Events

```py
e1 = event("e1", controllable = True)
e2 = event("e2", controllable = False)
e3 = event("e3", controllable = True)
e4 = event("e4", controllable = False)
```

### Creating an Automaton

```cs
G1 = dfa(
[
    (s1, e1, s2), 
    (s2, e2, s1)
], s1, "G1")
  
G2 = dfa(
[
    (s1, e3, s2), 
    (s2, e4, s1)
], s1, "G2");
```

## Operations with Automata

### Making a Parallel composition

```cs

Gp = parallel_composition(G1, G2); 

```
### Showing the Automaton

```cs
 show_automaton(Gp)
 ```
