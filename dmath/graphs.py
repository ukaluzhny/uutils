"""
subsystem, a dictionary: name -> list of node names
nodes, a dictionary: name -> [type, list of input names]
"""
import re
from os import listdir, mkdir, remove, chdir, getcwd
from os.path import isdir, join, exists, split, splitext


def graph_output(fname, subsystems, elements):
    nodes = ""
    edges = ""
    LG = 'LabelGraphics\n[\n configuration "CroppingLabel"\n autoSizePolicy "node_width"\nalignment "center"\n'
    formats = {
        "graph": #needs groups, nodes and edges
            'graph\n[\nhierarchic 1\ndirected 1\n{groups}\n{nodes}\n{edges}\n]', 
        "group": #needs [id, label], LG
            'node\n[\nid {}\nlabel "{}"\nisGroup 1\n'
            '{LG}fill "#CCFFFF"\n color "#333333"\n fontSize 20\n]\n]\n',
        "node": #needs shape, width, height, LG; then [id, label, group_id]
            'node\n[\nid {}\nlabel "{}"\ngid {}\n'
            'graphics\n[\n type "{shape}"\n w {width}.0\n h {height}.0\n]\n{LG}\n]\n]',
        "edge": 
            'edge\n[\nsource {}\ntarget {}\n'
            'graphics\n[\n smoothBends 1\n width 2\n targetArrow "standard"\n]\n]'
        }
        
    counter = 0
    for s in subsystems:
        nodes += formats["sub"].format(counter, s)
        sub_id = counter
        counter += 1
        for n in subsystems[s]:
            _type = elements[n][0]
            nodes += formats[_type].format(counter, n, sub_id)
            elements[n].append(counter)
            counter += 1
    for n in elements:
        print(n)
        n_id = elements[n][2]
        for s in elements[n][1]:
            edges += formats["edge"].format(elements[s][2], n_id)
    open(fname, "w"). write(formats["graph"].format(nodes, edges))

class Names(object):
    def __init__(self, start_nodes):
        self.dict = dict()
        for n in start_nodes: self.dict[n] = n
    def __call__(self, name):
        name = name.strip()
        if name in self.dict: name = self.dict[name]
        return name
    def add(self, old, new = None):
        if not new: new = old
        self.dict[old] = new
    def __contains__(self, name):
        return name in self.dict
    def __len__(self):
        return len(self.dict)
        
class Pattern(object):
    def __init__(self, split, cond, nodes, edges):
        self.split = split
        self.cond  = cond
        self.nodes = nodes
        self.edges = edges
    def __call__(self, s, names):
        operands = self.split(s)
        for i in range(len(operands)):
            operands[i] = names(operands[i])
        if self.cond(operands, names):
            nodes = self.nodes(operands, names)
            return nodes, self.edges(operands, nodes)
    
def tgf(fname, s, start_nodes, patterns):
    names = Names(start_nodes)
    all_edges = []
    for l in s.splitlines():
        print(l, end = ";   ")
        a, bc = l.split(' = ')
        a = a.strip()
        pattern_found = False
        for p in patterns:
            increment = p(bc, names)
            if increment:
                nodes, edges = increment
                for node in nodes: names.add(node)
                for edge in edges: all_edges.append(edge)
                pattern_found = True
                break
        if not pattern_found:
            bc = bc.strip()
            assert bc in names
            names.add(a, names(bc))
            print (a, bc)
        else:    
            names.add(a, nodes[0])
            print(a, nodes, edges)
    with open(fname+ ".tgf", 'w') as f:
        for n in names.dict: 
            print (n, n, file = f)
            if n != names.dict[n]: 
                all_edges.append((names.dict[n], n))
        print ('#', file = f)
        for e in all_edges: print (e[0], e[1], file = f)   

 # split, cond, nodes, edges 
def two_names(ops, names): 
    return len(ops) == 2 and ops[0] in names and ops[1] in names
    
