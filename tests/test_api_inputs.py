from pathlib import Path
import pytest
from ultrades import automata as ua, petrinets as pn


def model():
    q0, q1 = ua.state('q0', True), ua.state('q1')
    a, b = ua.event('a'), ua.event('b', False)
    return ua.dfa([[q0, a, q1], [q1, b, q0]], q0, 'G'), a


def test_event_forms_have_equivalent_projection():
    g, a = model()
    expected = ua.projection(g, [a])
    for value in (a, 'a', ['a'], iter([a])):
        result = ua.projection(g, value)
        assert len(ua.states(result)) == len(ua.states(expected))
        assert {str(e) for e in ua.events(result)} == {'b'}
    with pytest.raises(ValueError, match='Unknown event'):
        ua.projection(g, 'missing')


def test_generator_composition_and_single_plant_supervision():
    g, _ = model()
    assert ua.isomorphism(ua.parallel_composition(iter([g, g])), ua.parallel_composition(g, g))
    assert ua.isomorphism(ua.product(iter([g, g])), ua.product(g, g))
    assert ua.isomorphism(ua.monolithic_supervisor(g, g), ua.monolithic_supervisor([g], [g]))


def test_path_objects_roundtrip(tmp_path):
    g, _ = model()
    path = tmp_path / 'model.xml'
    ua.write_xml(g, path)
    assert ua.isomorphism(g, ua.read_xml(path))


def test_invalid_transition_has_python_error():
    q = ua.state('q')
    with pytest.raises(TypeError, match=r'transitions\[0\]'):
        ua.dfa([(q,)], q, 'bad')


def test_petri_mapping_and_legacy_counts():
    p, t = pn.place('p'), pn.transition('t')
    assert str(pn.marking({p: 2})) == str(pn.marking([(p, '2')]))
    net = pn.petri_net(iter([(p, t, 1)]), 'P')
    assert pn.is_siphon(net, p) == pn.is_siphon(net, [p])
    with pytest.raises(ValueError, match='token count'):
        pn.marking({p: -1})
    with pytest.raises(TypeError, match='connect'):
        pn.petri_net([(p, p, 1)], 'invalid')
