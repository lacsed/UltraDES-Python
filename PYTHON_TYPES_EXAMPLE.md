# Tipos Python com Conversão Transparente para C#

Este documento demonstra como usar os novos tipos Python (`PythonEvent`, `PythonState`, `PythonTransition`) que convertem automaticamente para tipos C# do UltraDES.

## Tipos Disponíveis

### 1. `PythonEvent` - Eventos
```python
from ultrades.automata import event

# Criar eventos mais facilmente em Python
e1 = event("alpha")  # Controlável por padrão
e2 = event("beta", controllable=False)  # Incontrolável

# Verificar propriedades
print(e1.controllable)  # True
print(e2.controllable)  # False
```

### 2. `PythonState` - Estados
```python
from ultrades.automata import state, is_marked

# Criar estados
q0 = state("q0")  # Não marcado por padrão
q1 = state("q1", marked=True)  # Marcado

# Verificar propriedades
print(q0.marked)  # False
print(q1.marked)  # True
print(is_marked(q1))  # True
```

### 3. `PythonTransition` - Transições
```python
from ultrades.automata import PythonTransition, state, event

# Criar transições facilmente
q0 = state("q0")
q1 = state("q1")
a = event("a")

# Criar transição - sintaxe Pythônica
t1 = PythonTransition(q0, a, q1)
```

## Usando Tipos Python com Autômatos

```python
from ultrades.automata import state, event, PythonTransition, dfa

# Criar estados
q0 = state("q0")
q1 = state("q1", marked=True)

# Criar eventos
a = event("a", controllable=True)
b = event("b", controllable=False)

# Criar transições com tipos Python
transitions = [
    PythonTransition(q0, a, q1),
    PythonTransition(q1, b, q0),
]

# Criar autômato - a conversão para C# é feita automaticamente
G = dfa(transitions, q0, "exemplo")
```

## Composição de Autômatos - Forma Antiga (compatível)

```python
from ultrades.automata import parallel_composition, product

# Forma original ainda funciona
G_par = parallel_composition(G1, G2)
G_prod = product(G1, G2)
```

## Composição de Autômatos - Nova Forma (com listas)

```python
from ultrades.automata import parallel_composition, product

# Agora você pode passar listas de autômatos!
G1, G2, G3 = ...  # autômatos

# Composição paralela de 3 autômatos
G_par = parallel_composition([G1, G2, G3])

# Produto de 4 autômatos
G_prod = product([G1, G2, G3, G4])
```

## Funções com Suporte a Tipos Python

### Observabilidade e Diagnosticabilidade
```python
from ultrades.automata import create_observer, is_diagnosable

# Usar PythonEvent em vez de strings ou tipos C#
unobservable = [event("alpha"), event("beta")]
observer = create_observer(G, unobservable)
diagnosable = is_diagnosable(observer)
```

### Projeção
```python
from ultrades.automata import projection

# Remover eventos usando PythonEvent
events_to_remove = [event("tau"), event("epsilon")]
G_proj = projection(G, events_to_remove)
```

### Opacidade
```python
from ultrades.automata import initial_state_opacity

# Usar tipos Python diretamente
unobservable = [event("secret1")]
secret_states = [state("s1"), state("s2")]

is_opaque, estimator = initial_state_opacity(G, unobservable, secret_states)
```

## Conversão Manual (quando necessário)

Se precisar converter manualmente para tipos C#:

```python
from ultrades.automata import PythonEvent, PythonState

# Converter para C# quando necessário
py_event = event("alpha")
csharp_event = py_event._to_csharp()

py_state = state("q0")
csharp_state = py_state._to_csharp()
```

## Benefícios

1. **Mais Pythônico**: Sintaxe mais natural para desenvolvedores Python
2. **Transparente**: Conversão automática para C# quando necessário
3. **Compatível**: Código antigo continua funcionando
4. **Legível**: Menos boilerplate, mais expressivo
5. **Type-safe**: Propriedades são acessíveis como atributos Python

## Exemplo Completo

```python
from ultrades.automata import (
    state, event, PythonTransition, dfa,
    parallel_composition, create_observer
)

# Criar primeiro autômato
q0 = state("q0")
q1 = state("q1", marked=True)
a = event("a")
b = event("b", controllable=False)

G1 = dfa([
    PythonTransition(q0, a, q1),
    PythonTransition(q1, b, q0),
], q0, "G1")

# Criar segundo autômato
p0 = state("p0")
p1 = state("p1", marked=True)
c = event("c")

G2 = dfa([
    PythonTransition(p0, c, p1),
    PythonTransition(p1, a, p0),
], p0, "G2")

# Composição com nova sintaxe
G_composed = parallel_composition([G1, G2])

# Observer com tipos Python
unobs = [event("secret")]
obs = create_observer(G_composed, unobs)
```
