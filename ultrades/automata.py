import clr
clr.AddReference("UltraDES")
clr.AddReference("System.Linq")
clr.AddReference('System.Collections')

from System import ValueTuple
from System.Collections.Generic import HashSet, List

from UltraDES import (
    AbstractEvent,
    Controllability,
    DeterministicFiniteAutomaton,
    Event,
    Marking,
    ObserverAlgorithms,
    State,
    Transition,
)
from UltraDES.Diagnosability import DiagnosticsAlgoritms
from UltraDES.Opacity import OpacityAlgorithms

def _bind_to_string(cls):
    def _to_string(self):
        return self.ToString()
    cls.__str__ = _to_string
    cls.__repr__ = _to_string


_bind_to_string(State)
_bind_to_string(Event)
_bind_to_string(Transition)

from IPython.core.display import HTML, Javascript, display
from IPython.core.getipython import get_ipython
import time
import hashlib


# === Python/.NET interop helpers ===
def _as_event(event_like, event_source):
    """Return the C# ``Event`` instance for ``event_like``."""

    if isinstance(event_like, AbstractEvent):
        return event_like

    if isinstance(event_like, str):
        if not event_source:
            raise TypeError(
                "Event names can only be resolved when an automaton is provided."
            )
        for candidate in event_source:
            name = getattr(candidate, "Name", None)
            if name == event_like or str(candidate) == event_like:
                return candidate
        raise ValueError(f"Unknown event '{event_like}'")

    raise TypeError(
        "Events must be UltraDES events or event names (strings) when using the Python wrapper."
    )


def _as_state(state_like, state_source):
    """Return the C# ``State`` instance for ``state_like``."""

    if isinstance(state_like, State):
        return state_like

    if isinstance(state_like, str):
        if not state_source:
            raise TypeError(
                "State names can only be resolved when an automaton is provided."
            )
        for candidate in state_source:
            name = getattr(candidate, "Name", None)
            if name == state_like or str(candidate) == state_like:
                return candidate
        raise ValueError(f"Unknown state '{state_like}'")

    raise TypeError(
        "States must be UltraDES states or state names (strings) when using the Python wrapper."
    )


def _normalize_source(source):
    if source is None:
        return None
    return list(source)


def _to_event_hashset(events, event_source=None):
    event_source = _normalize_source(event_source)
    hashset = HashSet[AbstractEvent]()
    for event in events:
        if event_source is None:
            if isinstance(event, AbstractEvent):
                hashset.Add(event)
            else:
                raise TypeError(
                    "Events must be UltraDES events when no automaton context is provided."
                )
        else:
            hashset.Add(_as_event(event, event_source))
    return hashset


def _to_state_list(states, state_source=None):
    state_source = _normalize_source(state_source)
    state_list = List[State]()
    for state in states:
        if state_source is None:
            if isinstance(state, State):
                state_list.Add(state)
            else:
                raise TypeError(
                    "States must be UltraDES states when no automaton context is provided."
                )
        else:
            state_list.Add(_as_state(state, state_source))
    return state_list


def _to_state_tuple_list(pairs, state_source=None):
    state_source = _normalize_source(state_source)
    tuple_type = ValueTuple[State, State]
    tuple_list = List[ValueTuple[State, State]]()
    for origin, destination in pairs:
        if state_source is None:
            if isinstance(origin, State) and isinstance(destination, State):
                resolved_origin = origin
                resolved_destination = destination
            else:
                raise TypeError(
                    "State pairs must contain UltraDES states when no automaton context is provided."
                )
        else:
            resolved_origin = _as_state(origin, state_source)
            resolved_destination = _as_state(destination, state_source)
        tuple_list.Add(tuple_type(resolved_origin, resolved_destination))
    return tuple_list


def load_viz_js():
    script = """
        var script = document.createElement('script');
        script.src = "https://github.com/mdaines/viz.js/releases/download/v1.8.1-pre.5/viz.js";
        document.head.appendChild(script);
    """
    display(Javascript(script))
    
load_viz_js()

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
    return list(G.Events)

def states(G):
    return list(G.States)

def marked_states(G):
    return list(G.MarkedStates)

def transitions(G):
    trans = G.Transitions
    return list(map(lambda t: (t.Origin, t.Trigger, t.Destination), trans))

def simplify_states_name(G):
    return G.SimplifyStatesName()

def to_regular_expression(G):
    return G.ToRegularExpression

# Operations
def parallel_composition(G1, G2):
    return DeterministicFiniteAutomaton.ParallelComposition(G1, G2)

def product(G1, G2):
    return DeterministicFiniteAutomaton.Product(G1, G2)

def projection(G, remove):
    return G.Projection(remove)

def inverse_projection(G, events):
    return G.InverseProjection(events)

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

def isomorphism(G1, G2):
    return DeterministicFiniteAutomaton.Isomorphism(G1, G2)

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

    return list(DeterministicFiniteAutomaton.LocalModularSupervisor(plants_lst, specs_lst, None))

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

def write_fm(G, path):
    G.ToFM(path)

def show_automaton(G):
    shell_type = get_ipython().__class__.__name__
    
    if shell_type == 'Shell':
        timestamp = str(time.time())
        hash_obj = hashlib.md5(timestamp.encode())
        div_id = "out_" + hash_obj.hexdigest()

        htmlContent = f'''
        <script src="https://github.com/mdaines/viz.js/releases/download/v1.8.1-pre.5/viz.js"></script>
        <div id="{div_id}"></div>
        <script>
            let targetDiv = document.querySelector("#{div_id}");
            targetDiv.innerHTML = Viz(`{G.ToDotCode.replace("rankdir=TB", "rankdir=LR")}`, 'svg');
        </script>
        '''

        return display(HTML(htmlContent))
    else:
        timestamp = str(time.time())
        hash_obj = hashlib.md5(timestamp.encode())
        div_id = "out_" + hash_obj.hexdigest()

        display(HTML(f'<div id="{div_id}"></div>'))

        code = f'''
        let targetDiv = document.querySelector("#{div_id}");
        targetDiv.innerHTML = Viz(`{G.ToDotCode.replace("rankdir=TB", "rankdir=LR")}`, 'svg')'''

        return Javascript(code)

# Observer Algorithms
def observer_property_verify(G, events):
    list_opv = ObserverAlgorithms.ObserverPropertyVerify(
        G, _to_event_hashset(events, G.Events)
    )
    return_on_dead = bool(list_opv[0])
    determinized_G = list_opv[1].Determinize

    return (return_on_dead, determinized_G)

def observer_property_search(G, events):
    return ObserverAlgorithms.ObserverPropertySearch(
        G, _to_event_hashset(events, G.Events)
    ).Determinize


# Diagnostics
def create_observer(G, unobservable_events):
    """Construct the observer automaton for ``G``.

    ``unobservable_events`` may contain :class:`Event` instances or event names.
    """

    return DiagnosticsAlgoritms.CreateObserver(
        G, _to_event_hashset(unobservable_events, G.Events)
    )


def is_diagnosable(observer):
    """Check whether the system represented by ``observer`` is diagnosable."""

    return bool(DiagnosticsAlgoritms.IsDiagnosable(observer))


# Opacity algorithms
def initial_state_opacity(G, unobservable_events, secret_states):
    """Evaluate initial-state opacity for ``G``.

    Both ``unobservable_events`` and ``secret_states`` accept UltraDES objects or
    their corresponding names. Returns ``(is_opaque, estimator)`` mirroring the
    C# API.
    """

    result, estimator = OpacityAlgorithms.InitialStateOpacity(
        G,
        _to_event_hashset(unobservable_events, G.Events),
        _to_state_list(secret_states, G.States),
    )
    return bool(result), estimator


def current_step_opacity(G, unobservable_events, secret_states):
    """Evaluate current-step opacity for ``G``.

    Parameters follow the same conventions as :func:`initial_state_opacity`.
    """

    result, estimator = OpacityAlgorithms.CurrentStepOpacity(
        G,
        _to_event_hashset(unobservable_events, G.Events),
        _to_state_list(secret_states, G.States),
    )
    return bool(result), estimator


def initial_final_state_opacity(G, unobservable_events, secret_state_pairs):
    """Evaluate infinite-step opacity for ``G``.

    ``secret_state_pairs`` may contain ``(State, State)`` tuples or state name
    pairs.
    """

    result, estimator = OpacityAlgorithms.InitialFinalStateOpacity(
        G,
        _to_event_hashset(unobservable_events, G.Events),
        _to_state_tuple_list(secret_state_pairs, G.States),
    )
    return bool(result), estimator


def k_steps_opacity(G, unobservable_events, secret_states, k):
    """Evaluate ``k``-steps opacity for ``G``.

    Parameters follow the same conventions as :func:`initial_state_opacity`.
    """

    result, estimator = OpacityAlgorithms.KStepsOpacity(
        G,
        _to_event_hashset(unobservable_events, G.Events),
        _to_state_list(secret_states, G.States),
        k,
    )
    return bool(result), estimator

