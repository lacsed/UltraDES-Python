from ultrades.automata import (
    accessible,
    dfa,
    event,
    events,
    initial_state,
    inverse_projection,
    is_controllable,
    is_marked,
    marked_states,
    observer_property_verify,
    parallel_composition,
    product,
    projection,
    state,
    states,
    transitions,
)


def _two_state_automaton(name="G"):
    s1 = state("s1", marked=True)
    s2 = state("s2", marked=False)
    e1 = event("e1", controllable=True)
    e2 = event("e2", controllable=False)
    return dfa([(s1, e1, s2), (s2, e2, s1)], s1, name), s1, s2, e1, e2


def test_state_and_event_flags():
    marked = state("marked", marked=True)
    unmarked = state("unmarked", marked=False)
    controllable = event("controllable", controllable=True)
    uncontrollable = event("uncontrollable", controllable=False)

    assert is_marked(marked) is True
    assert is_marked(unmarked) is False
    assert is_controllable(controllable) is True
    assert is_controllable(uncontrollable) is False


def test_dfa_accessors_return_expected_counts_and_wrappers():
    automaton, s1, _s2, e1, e2 = _two_state_automaton()

    assert str(initial_state(automaton)) == str(s1)
    assert {str(q) for q in states(automaton)} == {"s1", "s2"}
    assert {str(e) for e in events(automaton)} == {"e1", "e2"}
    assert [str(q) for q in marked_states(automaton)] == ["s1"]
    assert {(str(t[0]), str(t[1]), str(t[2])) for t in transitions(automaton)} == {
        ("s1", "e1", "s2"),
        ("s2", "e2", "s1"),
    }
    assert is_controllable(e1) is True
    assert is_controllable(e2) is False


def test_projection_accepts_single_event_and_event_list():
    automaton, _s1, _s2, e1, e2 = _two_state_automaton()

    projected_single = projection(automaton, e1)
    projected_list = projection(automaton, [e1])
    inverse = inverse_projection(projected_single, [e2])

    assert len(states(projected_single)) >= 1
    assert len(states(projected_list)) == len(states(projected_single))
    assert "e2" in {str(e) for e in events(inverse)}


def test_parallel_composition_and_product_counts():
    g1, s1, s2, _e1, _e2 = _two_state_automaton("G1")
    e3 = event("e3", controllable=True)
    e4 = event("e4", controllable=False)
    g2 = dfa([(s1, e3, s2), (s2, e4, s1)], s1, "G2")

    composed = parallel_composition(g1, g2)
    multiplied = product(g1, composed)

    assert len(states(composed)) == 4
    assert len(transitions(composed)) == 8
    assert len(states(multiplied)) >= 1


def test_accessible_and_observer_property_smoke():
    automaton, _s1, _s2, e1, _e2 = _two_state_automaton()

    accessible_part = accessible(automaton)
    observer_ok, observer = observer_property_verify(automaton, [e1])

    assert len(states(accessible_part)) == 2
    assert isinstance(observer_ok, bool)
    assert len(states(observer)) >= 1
