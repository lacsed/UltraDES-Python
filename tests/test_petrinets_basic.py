import ultrades.petrinets as pn


def _net():
    p1 = pn.place("p1")
    p2 = pn.place("p2")
    p3 = pn.place("p3")
    p4 = pn.place("p4")
    t1 = pn.transition("t1")
    t2 = pn.transition("t2")
    t3 = pn.transition("t3")
    net = pn.petri_net(
        [
            (t1, p4, 1),
            (t3, p1, 2),
            (t3, p4, 1),
            (t2, p1, 1),
            (p1, t1, 1),
            (p2, t2, 1),
            (p3, t3, 2),
        ],
        "P",
    )
    marking = pn.marking([(p1, 2), (p2, 3), (p3, 0), (p4, 1)])
    return net, marking, (p1, p2, p3, p4), (t1, t2, t3)


def test_petri_net_basic_counts_and_weights():
    net, _marking, (p1, _p2, _p3, p4), (t1, _t2, t3) = _net()

    assert len(pn.places(net)) == 4
    assert len(pn.transitions(net)) == 3
    assert len(pn.arcs(net)) == 7
    assert len(pn.inputs(net, p4)) == 2
    assert len(pn.outputs(net, p1)) == 1
    assert pn.weight(net, p1, t1) == 1
    assert pn.weight(net, t3, p1) == 2


def test_enabled_and_fire_transition():
    net, marking, (_p1, _p2, _p3, _p4), (t1, _t2, _t3) = _net()

    enabled = pn.enabled_transitions(net, marking)
    fired = pn.fire_transition(net, marking, t1)

    assert len(enabled) == 2
    assert "p1: 1" in str(fired)
    assert "p4: 2" in str(fired)
