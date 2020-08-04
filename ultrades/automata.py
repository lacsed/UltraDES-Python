import clr
clr.AddReference("UltraDES")
clr.AddReference("System.Linq")
clr.AddReference('System.Collections')

from System.Collections.Generic import List

from UltraDES import DeterministicFiniteAutomaton, State, Event, Marking, Controllability, Transition
from IPython.core.display import HTML, Javascript, display

def state(name, marked = False):
    return State(name, Marking.Marked if marked else Marking.Unmarked)

def is_marked(q):
    return q.Marking == Marking.Marked

def event(name, controllable = True):
    return Event(name, Controllability.Controllable if controllable else Controllability.Uncontrollable)

def is_controllable(e):
    return e.Controllability == Controllability.Controllable

# Automaton
def dfa(transitions, initial, name):
    trans = List[Transition]()
    for t in map(lambda t: Transition(t[0], t[1], t[2]), transitions):
        trans.Add(t)
    return DeterministicFiniteAutomaton(trans, initial, name)

def initial_state(G):
    return G.InitialState

def events(G):
    return G.Events

def states(G):
    return G.States

def marked_states(G):
    return G.MarkedStates

def transitions(G):
    trans = G.Transitions
    return list(map(lambda t: (t.Origin, t.Trigger, t.Destination), trans))

# Operations
def parallel_composition(G1, G2):
    return DeterministicFiniteAutomaton.ParallelComposition(G1, G2)

def product(G1, G2):
    return DeterministicFiniteAutomaton.Product(G1, G2)

def projection(G, remove):
    return G.Projection(remove)

def accessible(G):
    return G.AccessiblePart

def coaccessible(G):
    return G.CoaccessiblePart

def trim(G):
    return G.Trim

def minimize(G):
    return G.Minimal

def prefix_closure(G):
    return G.PrefixClosure        

# Supervisory Controle
def monolithic_supervisor(plants, specifications):
    plants_lst = List[DeterministicFiniteAutomaton]()
    for p in plants:
        plants_lst.Add(p)

    specs_lst = List[DeterministicFiniteAutomaton]()
    for e in specifications:
        specs_lst.Add(e)

    return DeterministicFiniteAutomaton.MonolithicSupervisor(plants_lst, specs_lst, True)

def local_modular_supervisors(plants, specifications):
    plants_lst = List[DeterministicFiniteAutomaton]()
    for p in plants:
        plants_lst.Add(p)

    specs_lst = List[DeterministicFiniteAutomaton]()
    for e in specifications:
        specs_lst.Add(e)

    return list(DeterministicFiniteAutomaton.LocalModularSupervisor(plants_lst, specs_lst))

def local_modular_reduced_supervisors(plants, specifications):
    plants_lst = List[DeterministicFiniteAutomaton]()
    for p in plants:
        plants_lst.Add(p)

    specs_lst = List[DeterministicFiniteAutomaton]()
    for e in specifications:
        specs_lst.Add(e)
     
    return list(DeterministicFiniteAutomaton.LocalModularReducedSupervisor(plants_lst, specs_lst))   
    
def local_modular_localized_supervisors(plants, specifications):
    plants_lst = List[DeterministicFiniteAutomaton]()
    for p in plants:
        plants_lst.Add(p)

    specs_lst = List[DeterministicFiniteAutomaton]()
    for e in specifications:
        specs_lst.Add(e)
     
    return list(DeterministicFiniteAutomaton.LocalModularLocalizedSupervisor(plants_lst, specs_lst))     

def localized_supervisors(plants, specifications):
    plants_lst = List[DeterministicFiniteAutomaton]()
    for p in plants:
        plants_lst.Add(p)

    specs_lst = List[DeterministicFiniteAutomaton]()
    for e in specifications:
        specs_lst.Add(e)
     
    return list(DeterministicFiniteAutomaton.MonolithicLocalizedSupervisor(plants_lst, specs_lst))

def monolithic_reduced_supervisor(plants, specifications):
    plants_lst = List[DeterministicFiniteAutomaton]()
    for p in plants:
        plants_lst.Add(p)

    specs_lst = List[DeterministicFiniteAutomaton]()
    for e in specifications:
        specs_lst.Add(e)

    return DeterministicFiniteAutomaton.MonolithicReducedSupervisor(plants_lst, specs_lst)    

# IO Operations

def read_ads(path):
    return DeterministicFiniteAutomaton.FromAdsFile(path)

def write_ads(G, path):
    G.ToAdsFile(path)

def read_fsm(path):
    return DeterministicFiniteAutomaton.FromFsmFile(path)

def write_fsm(G, path):
    G.ToFsmFile(path)

def read_wmod(path):
    plants, specs = DeterministicFiniteAutomaton.FromWmodFile(path, List[DeterministicFiniteAutomaton](), List[DeterministicFiniteAutomaton]())
    return (list(plants), list(specs))

def write_wmod(plants, specs, path):
    plants_lst = List[DeterministicFiniteAutomaton]()
    for p in plants:
        plants_lst.Add(p)

    specs_lst = List[DeterministicFiniteAutomaton]()
    for e in specs:
        specs_lst.Add(e)

    DeterministicFiniteAutomaton.ToWmodFile(path, plants_lst, specs_lst)

def read_xml(path, names = True):
    return DeterministicFiniteAutomaton.FromXMLFile(path, names)

def write_xml(G, path):
    G.ToXMLFile(path)

def read_bin(path):
    return DeterministicFiniteAutomaton.DeserializeAutomaton(path)

def write_bin(G, path):
    G.SerializeAutomaton(path)

def show_automaton(G):
    html_code = ("element.innerHTML += (Viz(`{}`))").format(G.ToDotCode.replace("rankdir=TB", "rankdir=LR"))
    return Javascript(html_code, lib="https://github.com/mdaines/viz.js/releases/download/v1.8.1-pre.5/viz.js")

 





