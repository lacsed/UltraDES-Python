from ultrades.automata import dfa, event, read_ads, read_fsm, read_xml, state, states, transitions, write_ads, write_fsm, write_xml


def _automaton():
    s1 = state("s1", marked=True)
    s2 = state("s2", marked=False)
    e1 = event("e1", controllable=True)
    e2 = event("e2", controllable=False)
    return dfa([(s1, e1, s2), (s2, e2, s1)], s1, "G1")


def test_ads_roundtrip_preserves_counts(tmp_path):
    path = tmp_path / "g1.ads"
    automaton = _automaton()

    write_ads(automaton, str(path))
    loaded = read_ads(str(path))

    assert len(states(loaded)) == 2
    assert len(transitions(loaded)) == 2


def test_fsm_roundtrip_preserves_counts(tmp_path):
    path = tmp_path / "g1.fsm"
    automaton = _automaton()

    write_fsm(automaton, str(path))
    loaded = read_fsm(str(path))

    assert len(states(loaded)) == 2
    assert len(transitions(loaded)) == 2


def test_xml_roundtrip_preserves_counts(tmp_path):
    path = tmp_path / "g1.xml"
    automaton = _automaton()

    write_xml(automaton, str(path))
    loaded = read_xml(str(path))

    assert len(states(loaded)) == 2
    assert len(transitions(loaded)) == 2
