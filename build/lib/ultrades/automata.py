import clr
from ultrades import add_ultrades_reference
add_ultrades_reference()
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


# === Python wrapper types with transparent C# conversion ===
class PythonEvent:
    """Python wrapper for UltraDES Event with transparent C# conversion."""
    
    def __init__(self, name, controllable=True):
        """Create a Python Event.
        
        Args:
            name: Event name (string)
            controllable: Boolean indicating if event is controllable (default: True)
        """
        self.name = name
        self.controllable = controllable
        self._csharp_event = None
    
    def _to_csharp(self):
        """Convert to C# Event (cached)."""
        if self._csharp_event is None:
            self._csharp_event = Event(
                self.name,
                Controllability.Controllable if self.controllable else Controllability.Uncontrollable
            )
        return self._csharp_event
    
    def __repr__(self):
        ctrl = "controllable" if self.controllable else "uncontrollable"
        return f"Event('{self.name}', {ctrl})"
    
    def __str__(self):
        return self.name


class PythonState:
    """Python wrapper for UltraDES State with transparent C# conversion."""
    
    def __init__(self, name, marked=False):
        """Create a Python State.
        
        Args:
            name: State name (string)
            marked: Boolean indicating if state is marked (default: False)
        """
        self.name = name
        self.marked = marked
        self._csharp_state = None
    
    def _to_csharp(self):
        """Convert to C# State (cached)."""
        if self._csharp_state is None:
            self._csharp_state = State(
                self.name,
                Marking.Marked if self.marked else Marking.Unmarked
            )
        return self._csharp_state
    
    def __repr__(self):
        mark = "marked" if self.marked else "unmarked"
        return f"State('{self.name}', {mark})"
    
    def __str__(self):
        return self.name


class PythonTransition:
    """Python wrapper for UltraDES Transition with transparent C# conversion."""
    
    def __init__(self, origin, trigger, destination):
        """Create a Python Transition.
        
        Args:
            origin: Origin state (PythonState or State)
            trigger: Triggering event (PythonEvent or Event)
            destination: Destination state (PythonState or State)
        """
        self.origin = origin
        self.trigger = trigger
        self.destination = destination
    
    def _to_csharp(self):
        """Convert to C# Transition."""
        origin = self.origin._to_csharp() if isinstance(self.origin, PythonState) else self.origin
        trigger = self.trigger._to_csharp() if isinstance(self.trigger, PythonEvent) else self.trigger
        destination = self.destination._to_csharp() if isinstance(self.destination, PythonState) else self.destination
        return Transition(origin, trigger, destination)
    
    def __repr__(self):
        return f"PythonTransition({self.origin} --{self.trigger}--> {self.destination})"


def _convert_event_to_csharp(event_obj):
    """Convert Event to C# Event if needed."""
    if isinstance(event_obj, PythonEvent):
        return event_obj._to_csharp()
    return event_obj


def _convert_state_to_csharp(state_obj):
    """Convert State to C# State if needed."""
    if isinstance(state_obj, PythonState):
        return state_obj._to_csharp()
    return state_obj


def _convert_transition_to_csharp(transition_obj):
    """Convert Transition to C# Transition if needed."""
    if isinstance(transition_obj, PythonTransition):
        return transition_obj._to_csharp()
    return transition_obj


def state(name, marked=False):
    """Create a Python State (new easy-to-use type).
    
    Args:
        name: State name (string)
        marked: Boolean indicating if state is marked (default: False)
    
    Returns:
        PythonState: A Python wrapper state that converts transparently to C#
    """
    return PythonState(name, marked)


def is_marked(q):
    """Check if a state is marked.
    
    Args:
        q: State (PythonState or C# State)
    
    Returns:
        Boolean: True if marked, False otherwise
    """
    if isinstance(q, PythonState):
        return q.marked
    return q.Marking == Marking.Marked


def event(name, controllable=True):
    """Create a Python Event (new easy-to-use type).
    
    Args:
        name: Event name (string)
        controllable: Boolean indicating if event is controllable (default: True)
    
    Returns:
        PythonEvent: A Python wrapper event that converts transparently to C#
    """
    return PythonEvent(name, controllable)


def is_controllable(e):
    """Check if an event is controllable.
    
    Args:
        e: Event (PythonEvent or C# Event)
    
    Returns:
        Boolean: True if controllable, False otherwise
    """
    if isinstance(e, PythonEvent):
        return e.controllable
    return e.Controllability == Controllability.Controllable

# Automaton
def dfa(transitions, initial, name):
    """Create a Deterministic Finite Automaton.
    
    Args:
        transitions: List of transitions (PythonTransition or C# Transition)
        initial: Initial state (PythonState or C# State)
        name: Automaton name (string)
    
    Returns:
        DeterministicFiniteAutomaton: The created automaton
    """
    # Convert initial state if needed
    initial_csharp = _convert_state_to_csharp(initial)
    
    # Convert transitions
    trans = List[Transition]()
    for t in transitions:
        if isinstance(t, PythonTransition):
            trans.Add(t._to_csharp())
        else:
            trans.Add(t)
    
    return DeterministicFiniteAutomaton(trans, initial_csharp, name)

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
def parallel_composition(G1, G2=None):
    """Compute the parallel composition of automata.
    
    Can be called in two ways:
    1. parallel_composition(G1, G2) - Two automata (backward compatible)
    2. parallel_composition([G1, G2, ...]) - List of automata
    
    Args:
        G1: First automaton or list of automata
        G2: Second automaton (optional, for backward compatibility)
    
    Returns:
        DeterministicFiniteAutomaton: The parallel composition
    """
    # Handle list input
    if G2 is None and isinstance(G1, (list, tuple)):
        if len(G1) == 0:
            raise ValueError("At least one automaton is required")
        if len(G1) == 1:
            return G1[0]
        
        # Compute parallel composition of all automata
        result = G1[0]
        for automaton in G1[1:]:
            result = DeterministicFiniteAutomaton.ParallelComposition(result, automaton)
        return result
    
    # Handle two automata input (backward compatible)
    if G2 is None:
        raise TypeError("parallel_composition requires either 2 automata or a list of automata")
    
    return DeterministicFiniteAutomaton.ParallelComposition(G1, G2)


def product(G1, G2=None):
    """Compute the product of automata.
    
    Can be called in two ways:
    1. product(G1, G2) - Two automata (backward compatible)
    2. product([G1, G2, ...]) - List of automata
    
    Args:
        G1: First automaton or list of automata
        G2: Second automaton (optional, for backward compatibility)
    
    Returns:
        DeterministicFiniteAutomaton: The product
    """
    # Handle list input
    if G2 is None and isinstance(G1, (list, tuple)):
        if len(G1) == 0:
            raise ValueError("At least one automaton is required")
        if len(G1) == 1:
            return G1[0]
        
        # Compute product of all automata
        result = G1[0]
        for automaton in G1[1:]:
            result = DeterministicFiniteAutomaton.Product(result, automaton)
        return result
    
    # Handle two automata input (backward compatible)
    if G2 is None:
        raise TypeError("product requires either 2 automata or a list of automata")
    
    return DeterministicFiniteAutomaton.Product(G1, G2)

def projection(G, remove):
    """Compute the projection of an automaton.
    
    Args:
        G: Automaton to project
        remove: List of events to remove (PythonEvent or Event objects)
    
    Returns:
        DeterministicFiniteAutomaton: The projected automaton
    """
    # Convert PythonEvent to C# Event if needed
    remove_converted = HashSet[AbstractEvent]()
    if remove:
        for evt in remove:
            csharp_evt = _convert_event_to_csharp(evt)
            remove_converted.Add(csharp_evt)
    
    return G.Projection(remove_converted)


def inverse_projection(G, events):
    """Compute the inverse projection of an automaton.
    
    Args:
        G: Automaton to project
        events: List of events to project (PythonEvent or Event objects)
    
    Returns:
        DeterministicFiniteAutomaton: The inverse projected automaton
    """
    # Convert PythonEvent to C# Event if needed
    events_converted = HashSet[AbstractEvent]()
    if events:
        for evt in events:
            csharp_evt = _convert_event_to_csharp(evt)
            events_converted.Add(csharp_evt)
    
    return G.InverseProjection(events_converted)

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
    """Verify observer property on automaton.
    
    Args:
        G: Automaton to verify
        events: List of events to check (PythonEvent or Event objects)
    
    Returns:
        Tuple: (return_on_dead, determinized_observer)
    """
    # Convert events
    events_hashset = HashSet[AbstractEvent]()
    for evt in events:
        if isinstance(evt, PythonEvent):
            events_hashset.Add(evt._to_csharp())
        else:
            events_hashset.Add(_as_event(evt, G.Events))
    
    list_opv = ObserverAlgorithms.ObserverPropertyVerify(G, events_hashset)
    return_on_dead = bool(list_opv[0])
    determinized_G = list_opv[1].Determinize

    return (return_on_dead, determinized_G)


def observer_property_search(G, events):
    """Search for observer property on automaton.
    
    Args:
        G: Automaton to search
        events: List of events to check (PythonEvent or Event objects)
    
    Returns:
        DeterministicFiniteAutomaton: The determinized observer
    """
    # Convert events
    events_hashset = HashSet[AbstractEvent]()
    for evt in events:
        if isinstance(evt, PythonEvent):
            events_hashset.Add(evt._to_csharp())
        else:
            events_hashset.Add(_as_event(evt, G.Events))
    
    return ObserverAlgorithms.ObserverPropertySearch(G, events_hashset).Determinize


# Diagnostics
def create_observer(G, unobservable_events):
    """Construct the observer automaton for ``G``.

    ``unobservable_events`` may contain :class:`PythonEvent`, :class:`Event` instances 
    or event names (strings).
    
    Args:
        G: Automaton to create observer for
        unobservable_events: List of unobservable events
    
    Returns:
        DeterministicFiniteAutomaton: The observer automaton
    """
    # Convert PythonEvent and event names to C# Event
    events_hashset = HashSet[AbstractEvent]()
    for evt in unobservable_events:
        if isinstance(evt, PythonEvent):
            events_hashset.Add(evt._to_csharp())
        else:
            events_hashset.Add(_as_event(evt, G.Events))
    
    return DiagnosticsAlgoritms.CreateObserver(G, events_hashset)


def is_diagnosable(observer):
    """Check whether the system represented by ``observer`` is diagnosable."""

    return bool(DiagnosticsAlgoritms.IsDiagnosable(observer))


# Opacity algorithms
def initial_state_opacity(G, unobservable_events, secret_states):
    """Evaluate initial-state opacity for ``G``.

    Both ``unobservable_events`` and ``secret_states`` accept :class:`PythonEvent`,
    :class:`PythonState`, UltraDES objects or their corresponding names (strings).
    Returns ``(is_opaque, estimator)`` mirroring the C# API.
    
    Args:
        G: Automaton to check
        unobservable_events: List of unobservable events
        secret_states: List of secret states
    
    Returns:
        Tuple: (is_opaque, estimator)
    """
    # Convert unobservable events
    events_hashset = HashSet[AbstractEvent]()
    for evt in unobservable_events:
        if isinstance(evt, PythonEvent):
            events_hashset.Add(evt._to_csharp())
        else:
            events_hashset.Add(_as_event(evt, G.Events))
    
    # Convert secret states
    states_list = List[State]()
    for st in secret_states:
        if isinstance(st, PythonState):
            states_list.Add(st._to_csharp())
        else:
            states_list.Add(_as_state(st, G.States))

    result, estimator = OpacityAlgorithms.InitialStateOpacity(
        G, events_hashset, states_list
    )
    return bool(result), estimator


def current_step_opacity(G, unobservable_events, secret_states):
    """Evaluate current-step opacity for ``G``.

    Parameters follow the same conventions as :func:`initial_state_opacity`.
    
    Args:
        G: Automaton to check
        unobservable_events: List of unobservable events
        secret_states: List of secret states
    
    Returns:
        Tuple: (is_opaque, estimator)
    """
    # Convert unobservable events
    events_hashset = HashSet[AbstractEvent]()
    for evt in unobservable_events:
        if isinstance(evt, PythonEvent):
            events_hashset.Add(evt._to_csharp())
        else:
            events_hashset.Add(_as_event(evt, G.Events))
    
    # Convert secret states
    states_list = List[State]()
    for st in secret_states:
        if isinstance(st, PythonState):
            states_list.Add(st._to_csharp())
        else:
            states_list.Add(_as_state(st, G.States))

    result, estimator = OpacityAlgorithms.CurrentStepOpacity(
        G, events_hashset, states_list
    )
    return bool(result), estimator


def initial_final_state_opacity(G, unobservable_events, secret_state_pairs):
    """Evaluate infinite-step opacity for ``G``.

    ``secret_state_pairs`` may contain ``(PythonState, PythonState)``, ``(State, State)`` 
    tuples or state name pairs.
    
    Args:
        G: Automaton to check
        unobservable_events: List of unobservable events
        secret_state_pairs: List of (origin, destination) state pairs
    
    Returns:
        Tuple: (is_opaque, estimator)
    """
    # Convert unobservable events
    events_hashset = HashSet[AbstractEvent]()
    for evt in unobservable_events:
        if isinstance(evt, PythonEvent):
            events_hashset.Add(evt._to_csharp())
        else:
            events_hashset.Add(_as_event(evt, G.Events))
    
    # Convert state pairs
    tuple_type = ValueTuple[State, State]
    tuple_list = List[ValueTuple[State, State]]()
    for origin, destination in secret_state_pairs:
        origin_csharp = origin._to_csharp() if isinstance(origin, PythonState) else _as_state(origin, G.States)
        dest_csharp = destination._to_csharp() if isinstance(destination, PythonState) else _as_state(destination, G.States)
        tuple_list.Add(tuple_type(origin_csharp, dest_csharp))

    result, estimator = OpacityAlgorithms.InitialFinalStateOpacity(
        G, events_hashset, tuple_list
    )
    return bool(result), estimator


def k_steps_opacity(G, unobservable_events, secret_states, k):
    """Evaluate ``k``-steps opacity for ``G``.

    Parameters follow the same conventions as :func:`initial_state_opacity`.
    
    Args:
        G: Automaton to check
        unobservable_events: List of unobservable events
        secret_states: List of secret states
        k: Number of steps
    
    Returns:
        Tuple: (is_opaque, estimator)
    """
    # Convert unobservable events
    events_hashset = HashSet[AbstractEvent]()
    for evt in unobservable_events:
        if isinstance(evt, PythonEvent):
            events_hashset.Add(evt._to_csharp())
        else:
            events_hashset.Add(_as_event(evt, G.Events))
    
    # Convert secret states
    states_list = List[State]()
    for st in secret_states:
        if isinstance(st, PythonState):
            states_list.Add(st._to_csharp())
        else:
            states_list.Add(_as_state(st, G.States))

    result, estimator = OpacityAlgorithms.KStepsOpacity(
        G, events_hashset, states_list, k
    )
    return bool(result), estimator

