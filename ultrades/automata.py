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

    if isinstance(event_like, PythonEvent):
        return event_like._to_csharp()

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

    if isinstance(state_like, PythonState):
        return state_like._to_csharp()

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
            if isinstance(event, PythonEvent):
                hashset.Add(event._to_csharp())
            elif isinstance(event, AbstractEvent):
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
            if isinstance(state, PythonState):
                state_list.Add(state._to_csharp())
            elif isinstance(state, State):
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
            if isinstance(origin, (PythonState, State)) and isinstance(
                destination, (PythonState, State)
            ):
                resolved_origin = _convert_state_to_csharp(origin)
                resolved_destination = _convert_state_to_csharp(destination)
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


# === Python facade types with transparent C# conversion ===
class PythonEvent:
    """Python facade for an UltraDES C# ``Event``.

    The facade keeps the original C# object internally, exposes Python-friendly
    attributes and renders the event by name when printed.
    """

    def __init__(self, name, controllable=True):
        if isinstance(name, PythonEvent):
            self._csharp_event = name._to_csharp()
        elif isinstance(name, AbstractEvent):
            self._csharp_event = name
        else:
            self._csharp_event = Event(
                str(name),
                Controllability.Controllable
                if controllable
                else Controllability.Uncontrollable,
            )

    @property
    def name(self):
        return self._csharp_event.Name

    @property
    def controllable(self):
        return self._csharp_event.Controllability == Controllability.Controllable

    def _to_csharp(self):
        return self._csharp_event

    def __getattr__(self, name):
        return getattr(self._csharp_event, name)

    def __repr__(self):
        ctrl = "controllable" if self.controllable else "uncontrollable"
        return f"Event('{self.name}', {ctrl})"

    def __str__(self):
        return self.name

    def __eq__(self, other):
        return self._to_csharp().Equals(_convert_event_to_csharp(other))

    def __hash__(self):
        return self._to_csharp().GetHashCode()


class PythonState:
    """Python facade for an UltraDES C# ``State``."""

    def __init__(self, name, marked=False):
        if isinstance(name, PythonState):
            self._csharp_state = name._to_csharp()
        elif isinstance(name, State):
            self._csharp_state = name
        else:
            self._csharp_state = State(
                str(name), Marking.Marked if marked else Marking.Unmarked
            )

    @property
    def name(self):
        return self._csharp_state.Name

    @property
    def marked(self):
        return self._csharp_state.Marking == Marking.Marked

    def _to_csharp(self):
        return self._csharp_state

    def __getattr__(self, name):
        return getattr(self._csharp_state, name)

    def __repr__(self):
        mark = "marked" if self.marked else "unmarked"
        return f"State('{self.name}', {mark})"

    def __str__(self):
        return self.name

    def __eq__(self, other):
        return self._to_csharp().Equals(_convert_state_to_csharp(other))

    def __hash__(self):
        return self._to_csharp().GetHashCode()


class PythonTransition:
    """Python facade for an UltraDES C# ``Transition``."""

    def __init__(self, origin, trigger=None, destination=None):
        if trigger is None and destination is None:
            if isinstance(origin, PythonTransition):
                self._csharp_transition = origin._to_csharp()
            elif isinstance(origin, Transition):
                self._csharp_transition = origin
            else:
                raise TypeError(
                    "A transition facade needs either a Transition or "
                    "(origin, trigger, destination)."
                )
        else:
            self._csharp_transition = Transition(
                _convert_state_to_csharp(origin),
                _convert_event_to_csharp(trigger),
                _convert_state_to_csharp(destination),
            )

    @property
    def origin(self):
        return PythonState(self._csharp_transition.Origin)

    @property
    def trigger(self):
        return PythonEvent(self._csharp_transition.Trigger)

    @property
    def destination(self):
        return PythonState(self._csharp_transition.Destination)

    def _to_csharp(self):
        return self._csharp_transition

    def __getattr__(self, name):
        return getattr(self._csharp_transition, name)

    def __repr__(self):
        return f"Transition({self.origin} --{self.trigger}--> {self.destination})"

    def __str__(self):
        return f"{self.origin} --{self.trigger}--> {self.destination}"

    def __eq__(self, other):
        return self._to_csharp().Equals(_convert_transition_to_csharp(other))

    def __hash__(self):
        return self._to_csharp().GetHashCode()


def _convert_event_to_csharp(event_obj):
    """Convert a Python/C# event facade to the underlying C# Event."""
    if isinstance(event_obj, PythonEvent):
        return event_obj._to_csharp()
    return event_obj


def _convert_state_to_csharp(state_obj):
    """Convert a Python/C# state facade to the underlying C# State."""
    if isinstance(state_obj, PythonState):
        return state_obj._to_csharp()
    return state_obj


def _convert_transition_to_csharp(transition_obj):
    """Convert a Python/C# transition facade to the underlying C# Transition."""
    if isinstance(transition_obj, PythonTransition):
        return transition_obj._to_csharp()
    return transition_obj


def _wrap_event(event_obj):
    return event_obj if isinstance(event_obj, PythonEvent) else PythonEvent(event_obj)


def _wrap_state(state_obj):
    return state_obj if isinstance(state_obj, PythonState) else PythonState(state_obj)


def _wrap_transition(transition_obj):
    return (
        transition_obj
        if isinstance(transition_obj, PythonTransition)
        else PythonTransition(transition_obj)
    )


def state(name, marked=False):
    """Create or wrap a Python state facade."""
    return PythonState(name, marked)


def is_marked(q):
    """Check if a Python or C# state is marked."""
    return _convert_state_to_csharp(q).Marking == Marking.Marked


def event(name, controllable=True):
    """Create or wrap a Python event facade."""
    return PythonEvent(name, controllable)


def is_controllable(e):
    """Check if a Python or C# event is controllable."""
    return _convert_event_to_csharp(e).Controllability == Controllability.Controllable

# Automaton
def dfa(transitions, initial, name):
    """Create a Deterministic Finite Automaton.
    
    Args:
        transitions: List of transitions. Can be:
                     - PythonTransition objects
                     - Tuples (origin, event, destination)
                     - C# Transition objects
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
            # Convert PythonTransition to C# Transition
            trans.Add(t._to_csharp())
        elif isinstance(t, tuple) and len(t) == 3:
            # Handle tuple format (origin, event, destination) - backward compatible
            origin, event_obj, destination = t
            origin_csharp = _convert_state_to_csharp(origin)
            event_csharp = _convert_event_to_csharp(event_obj)
            destination_csharp = _convert_state_to_csharp(destination)
            trans.Add(Transition(origin_csharp, event_csharp, destination_csharp))
        else:
            # Assume it's a C# Transition
            trans.Add(_convert_transition_to_csharp(t))
    
    return DeterministicFiniteAutomaton(trans, initial_csharp, name)

def initial_state(G):
    return _wrap_state(G.InitialState)

def events(G):
    return [_wrap_event(e) for e in G.Events]

def states(G):
    return [_wrap_state(q) for q in G.States]

def marked_states(G):
    return [_wrap_state(q) for q in G.MarkedStates]

def transitions(G):
    return [_wrap_transition(t) for t in G.Transitions]

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

