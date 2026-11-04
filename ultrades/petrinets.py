import clr
from ultrades import add_ultrades_reference
add_ultrades_reference()
clr.AddReference("System.Linq")
clr.AddReference('System.Collections')

from System.Collections.Generic import List, KeyValuePair
from System import ValueTuple, UInt32

from UltraDES.PetriNets import PetriNet, Marking, Node, Place, Transition, Arc
from IPython.display import HTML, Javascript, display
from IPython.core.getipython import get_ipython
import time
from collections.abc import Mapping
import hashlib

def load_viz_js():
    script = """
        var script = document.createElement('script');
        script.src = "https://github.com/mdaines/viz.js/releases/download/v1.8.1-pre.5/viz.js";
        document.head.appendChild(script);
    """
    display(Javascript(script))


def place(name):
    return Place(name)

def transition(name):
    return Transition(name)

def _count(value, argument):
    # Preserve Python/.NET integers and numeric strings accepted by UInt32.Parse.
    try:
        return UInt32.Parse(str(value))
    except Exception as exc:
        raise ValueError(f"{argument} must be a nonnegative UInt32 integer") from exc


def marking(pairs):
    """Create a marking from (place, token count) pairs or a mapping.

    Counts must be nonnegative integers representable by UInt32.
    """
    marking_lst = List[KeyValuePair[Place, UInt32]]()
    items = pairs.items() if isinstance(pairs, Mapping) else pairs
    for index, item in enumerate(items):
        try:
            place_obj, count = item
        except (TypeError, ValueError) as exc:
            raise TypeError(f"pairs[{index}] must be (place, token count)") from exc
        if not isinstance(place_obj, Place):
            raise TypeError(f"pairs[{index}] must refer to a Place")
        marking_lst.Add(KeyValuePair[Place, UInt32](place_obj, _count(count, f"pairs[{index}] token count")))
    return Marking(marking_lst)


def petri_net(arcs, name):
    """Create a net from Arc objects or (origin, destination, weight) triples."""
    arcs_lst = List[Arc]()
    for index, item in enumerate(arcs):
        if isinstance(item, Arc):
            arcs_lst.Add(item)
            continue
        try:
            origin, destination, weight = item
        except (TypeError, ValueError) as exc:
            raise TypeError(f"arcs[{index}] must be an Arc or (origin, destination, weight)") from exc
        if not ((isinstance(origin, Place) and isinstance(destination, Transition)) or
                (isinstance(origin, Transition) and isinstance(destination, Place))):
            raise TypeError(f"arcs[{index}] must connect a Place and a Transition")
        arcs_lst.Add(Arc(origin, destination, _count(weight, f"arcs[{index}] weight")))
    return PetriNet(arcs_lst, name)

def places(P):
    return list(P.Places)

def transitions(P):
    return list(P.Transitions)

def arcs(P):
    return list(P.Arcs)

def inputs(P, b):
    return list(P.Inputs(b))

def outputs(P, b):
    return list(P.Outputs(b))

def weight(P, x, y):
    return P.Weight(x,y)  

def enabled_transitions(P, marking):
    return list(P.EnabledTransitions(marking))

def fire_transition(P, marking, transitions):
    return P.Fire(marking, transitions)

def is_siphon(P, places):
    places_lst = List[Place]()
    for p in ([places] if isinstance(places, Place) else places):
        places_lst.Add(p)

    return P.IsSiphon(places_lst)

def is_trap(P, places):
    places_lst = List[Place]()
    for p in ([places] if isinstance(places, Place) else places):
        places_lst.Add(p)

    return P.IsTrap(places_lst)

def coverability_tree(P, marking):
    return list(P.CoverabilityTree(marking))   

def coverability_graph(P, marking):
    return list(P.CoverabilityGraph(marking)) 

def reachability_tree(P, marking):
    return list(P.ReachabilityTree(marking))   

def incidence_matrix(P):
    return P.IncidenceMatrix();  

def show_petri_net(P):
    ipython = get_ipython()
    shell_type = ipython.__class__.__name__ if ipython is not None else None
    
    if shell_type == 'Shell':
        timestamp = str(time.time())
        hash_obj = hashlib.md5(timestamp.encode())
        div_id = "out_" + hash_obj.hexdigest()

        htmlContent = f'''
        <div id="{div_id}"></div>
        <script>
            let targetDiv = document.querySelector("#{div_id}");
            const renderPetriNet = () => {{
                targetDiv.innerHTML = Viz(`{P.ToDotCode().replace("rankdir=TB", "rankdir=LR")}`, 'svg');
            }};
            if (typeof Viz === "undefined") {{
                const script = document.createElement("script");
                script.src = "https://github.com/mdaines/viz.js/releases/download/v1.8.1-pre.5/viz.js";
                script.onload = renderPetriNet;
                document.head.appendChild(script);
            }} else {{
                renderPetriNet();
            }}
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
        const renderPetriNet = () => {{
            targetDiv.innerHTML = Viz(`{P.ToDotCode().replace("rankdir=TB", "rankdir=LR")}`, 'svg');
        }};
        if (typeof Viz === "undefined") {{
            const script = document.createElement("script");
            script.src = "https://github.com/mdaines/viz.js/releases/download/v1.8.1-pre.5/viz.js";
            script.onload = renderPetriNet;
            document.head.appendChild(script);
        }} else {{
            renderPetriNet();
        }}'''

        return Javascript(code)
