import clr
clr.AddReference("UltraDES")
clr.AddReference("System.Linq")
clr.AddReference('System.Collections')

from System.Collections.Generic import List, KeyValuePair
from System import ValueTuple, UInt32

from UltraDES.PetriNets import PetriNet, Marking, Node, Place, Transition, Arc
from IPython.core.display import HTML, Javascript, display
from IPython.core.getipython import get_ipython
import time
import hashlib

def load_viz_js():
    script = """
        var script = document.createElement('script');
        script.src = "https://github.com/mdaines/viz.js/releases/download/v1.8.1-pre.5/viz.js";
        document.head.appendChild(script);
    """
    display(Javascript(script))

load_viz_js()


def place(name):
    return Place(name)

def transition(name):
    return Transition(name)

def marking(pairs):
    marking_lst = List[KeyValuePair[Place, UInt32]]()
    for m in pairs:
        t = KeyValuePair[Place, UInt32](m[0], UInt32.Parse(str(m[1])))
        marking_lst.Add(t)

    return Marking(marking_lst)    

def petri_net(arcs, name):
    arcs_lst = List[Arc]()
    for a in arcs:
        t = Arc(a[0], a[1], a[2])
        arcs_lst.Add(t)
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
    return P.Fire(marking, transition)

def is_siphon(P, places):
    return P.IsSiphon(places)

def is_trap(P, places):
    return P.IsTrap(places)

def coverability_tree(P, marking):
    return list(P.CoverabilityTree(marking))   

def coverability_graph(P, marking):
    return list(P.CoverabilityGraph(marking)) 

def reachability_tree(P, marking):
    return list(P.ReachabilityTree(marking))   

def incidence_matrix(P):
    return P.IncidenceMatrix();  

def show_petri_net(P):
    shell_type = get_ipython().__class__.__name__
    
    if shell_type == 'Shell':
        html_code = ('''
        <script src="/nbextensions/google.colab/viz.js"></script>
        <script>
        var elem = document.createElement('svg');
        elem.innerHTML += (Viz(`{}`, `svg`));
        document.querySelector('#output-area').appendChild(elem);
        </script>
        ''').format(P.ToDotCode().replace("rankdir=TB", "rankdir=LR"))

        return HTML(html_code)
    else:
        timestamp = str(time.time())
        hash_obj = hashlib.md5(timestamp.encode())
        div_id = "out_" + hash_obj.hexdigest()

        display(HTML(f'<div id="{div_id}"></div>'))

        code = f'''
        let targetDiv = document.querySelector("#{div_id}");
        targetDiv.innerHTML = Viz(`{P.ToDotCode().replace("rankdir=TB", "rankdir=LR")}`, 'svg')'''

        return Javascript(code)
