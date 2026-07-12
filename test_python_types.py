"""
Test file to validate Python types and new function signatures.
"""

from ultrades.automata import (
    state, event, PythonTransition, PythonEvent, PythonState,
    dfa, parallel_composition, product,
    is_marked, is_controllable,
    initial_state, events, states, marked_states, projection
)


def test_python_event():
    """Test PythonEvent creation and properties."""
    print("\n=== Testing PythonEvent ===")
    
    e1 = event("alpha")
    e2 = event("beta", controllable=False)
    
    print(f"Event 1: {e1}")
    print(f"  Controllable: {e1.controllable}")
    
    print(f"Event 2: {e2}")
    print(f"  Controllable: {e2.controllable}")
    
    # Test C# conversion
    csharp_e1 = e1._to_csharp()
    print(f"C# conversion successful: {csharp_e1}")


def test_python_state():
    """Test PythonState creation and properties."""
    print("\n=== Testing PythonState ===")
    
    q0 = state("q0")
    q1 = state("q1", marked=True)
    
    print(f"State 0: {q0}")
    print(f"  Marked: {q0.marked}")
    
    print(f"State 1: {q1}")
    print(f"  Marked: {q1.marked}")
    
    # Test is_marked
    print(f"is_marked(q0): {is_marked(q0)}")
    print(f"is_marked(q1): {is_marked(q1)}")
    
    # Test C# conversion
    csharp_q0 = q0._to_csharp()
    print(f"C# conversion successful: {csharp_q0}")


def test_python_transition():
    """Test PythonTransition creation."""
    print("\n=== Testing PythonTransition ===")
    
    q0 = state("q0")
    q1 = state("q1")
    a = event("a")
    
    t = PythonTransition(q0, a, q1)
    print(f"Transition: {t}")
    
    # Test C# conversion
    csharp_t = t._to_csharp()
    print(f"C# conversion successful: {csharp_t}")


def test_dfa_with_python_types():
    """Test DFA creation with Python types."""
    print("\n=== Testing DFA with Python Types ===")
    
    # Create states
    q0 = state("q0")
    q1 = state("q1", marked=True)
    
    # Create events
    a = event("a", controllable=True)
    b = event("b", controllable=False)
    
    # Create transitions
    transitions = [
        PythonTransition(q0, a, q1),
        PythonTransition(q1, b, q0),
    ]
    
    # Create DFA
    G = dfa(transitions, q0, "TestAutomaton")
    print(f"DFA created: {G}")
    print(f"Initial state: {G.InitialState}")
    print(f"Number of states: {len(list(G.States))}")
    print(f"Wrapped initial state: {initial_state(G)}")
    print(f"Wrapped states: {states(G)}")
    print(f"Wrapped events: {events(G)}")
    print(f"Wrapped marked states: {marked_states(G)}")
    projected = projection(G, a)
    print(f"Projection with a single Python event: {projected}")


def test_parallel_composition_list():
    """Test parallel_composition with list."""
    print("\n=== Testing parallel_composition with List ===")
    
    # Create first automaton
    q0 = state("q0")
    q1 = state("q1", marked=True)
    a = event("a")
    G1 = dfa([PythonTransition(q0, a, q1)], q0, "G1")
    
    # Create second automaton
    p0 = state("p0")
    p1 = state("p1", marked=True)
    b = event("b")
    G2 = dfa([PythonTransition(p0, b, p1)], p0, "G2")
    
    # Test with list (new way)
    G_list = parallel_composition([G1, G2])
    print(f"Parallel composition (list): {G_list}")
    print(f"Number of states: {len(list(G_list.States))}")
    
    # Test backward compatibility (two arguments)
    G_compat = parallel_composition(G1, G2)
    print(f"Parallel composition (old way): {G_compat}")


def test_product_list():
    """Test product with list."""
    print("\n=== Testing product with List ===")
    
    # Create first automaton
    q0 = state("q0")
    q1 = state("q1", marked=True)
    a = event("a")
    G1 = dfa([PythonTransition(q0, a, q1)], q0, "G1")
    
    # Create second automaton
    p0 = state("p0")
    p1 = state("p1", marked=True)
    b = event("b")
    G2 = dfa([PythonTransition(p0, b, p1)], p0, "G2")
    
    # Test with list (new way)
    G_list = product([G1, G2])
    print(f"Product (list): {G_list}")
    print(f"Number of states: {len(list(G_list.States))}")
    
    # Test backward compatibility (two arguments)
    G_compat = product(G1, G2)
    print(f"Product (old way): {G_compat}")


def test_multiple_automata_composition():
    """Test composition with more than 2 automata."""
    print("\n=== Testing Composition with Multiple Automata ===")
    
    # Create 3 automata
    automata = []
    for i in range(3):
        q0 = state(f"q{i}_0")
        q1 = state(f"q{i}_1", marked=True)
        a = event(f"e{i}")
        G = dfa([PythonTransition(q0, a, q1)], q0, f"G{i}")
        automata.append(G)
    
    # Parallel composition of 3 automata
    G_par = parallel_composition(automata)
    print(f"Parallel composition of 3 automata: {G_par}")
    print(f"Number of states: {len(list(G_par.States))}")
    
    # Product of 3 automata
    G_prod = product(automata)
    print(f"Product of 3 automata: {G_prod}")
    print(f"Number of states: {len(list(G_prod.States))}")


if __name__ == "__main__":
    print("Testing Python Types and New Function Signatures")
    print("=" * 50)
    
    try:
        test_python_event()
        test_python_state()
        test_python_transition()
        test_dfa_with_python_types()
        test_parallel_composition_list()
        test_product_list()
        test_multiple_automata_composition()
        
        print("\n" + "=" * 50)
        print("All tests completed successfully!")
    except Exception as e:
        print(f"\nError during testing: {e}")
        import traceback
        traceback.print_exc()
