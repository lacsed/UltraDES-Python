from IPython.display import Javascript

from ultrades.automata import dfa, event, show_automaton, state
import ultrades.petrinets as pn


def test_show_automaton_returns_javascript_outside_ipython_shell():
    s1 = state("s1", marked=True)
    s2 = state("s2")
    e1 = event("e1")
    automaton = dfa([(s1, e1, s2)], s1, "G")

    rendered = show_automaton(automaton)

    assert isinstance(rendered, Javascript)
    assert "script.onload" in rendered.data
    assert "renderAutomaton" in rendered.data


def test_show_petri_net_returns_javascript_outside_ipython_shell():
    p1 = pn.place("p1")
    t1 = pn.transition("t1")
    net = pn.petri_net([(p1, t1, 1)], "P")

    rendered = pn.show_petri_net(net)

    assert isinstance(rendered, Javascript)
    assert "script.onload" in rendered.data
    assert "renderPetriNet" in rendered.data
