"""Graph related utilities


"""
import re
from os import listdir, mkdir, remove, chdir, getcwd
from os.path import isdir, join, exists, split, splitext
from itertools import chain
        
class Group(object):
    def __init__(self, label = "", properties = None):
        self.label = label
        self.properties = properties
        self.nodes = dict() #name -> properties
    def __repr__(self):
        return ', '.join([self.label, str(self.nodes)])
    def __setitem__(self, name, properties):
        self.nodes[name] = properties
    def __getitem__(self, name):
        return self.nodes[name]
    def __contains__(self, name):
        return (name in self.nodes)
    def __iter__(self):
        return iter(self.nodes)
class Graph(object):
    def __init__(self):
        self.groups = [dict()]
        self.edges = []
    def add_node(self, name, group = 0, properties = None):
        prev_group = self.group(name)
        if  prev_group != None:
            prev_properties = self.groups[prev_group].pop(name)
            assert not prev_properties or not properties
            assert not prev_group or not group
            group = group or prev_group
            properties = properties or prev_properties
            self.groups[group][name] = properties
        else:
            self.groups[group][name] = properties 
    def set_group(self, name, group):
        prev_group = self.group(name)
        properties = self.groups[prev_group].pop(name)
        self.groups[group][name] = properties
    def group(self, name):
        for i, group in enumerate(self.groups):
            if name in group: return i
    def add_edge(self, source, target, label = "", properties = None):
        self.edges.append((source, target, label, properties))
    def add_group(self, label = "", properties = None):
        self.groups.append(Group(label, properties))
    def gml(self, fname, graphics = None):
        graphics = graphics or (lambda x: "")  
        formats = {
            "graph": #needs groups, nodes and edges
                'graph\n[\nhierarchic 1\ndirected 1\n{}]\n', 
            "group": #needs id, name, graphics
                'node\n[\n\tid {}\n\tlabel "{}"\n\tisGroup 1\n\t{}\n]\n',
            "node": #needs id, name, group, graphics
                'node\n[\n\tid {}\n\tlabel "{}"\n\t{}{}\n]\n',
            "edge": #needs source_id, target_id, name, graphics
                'edge\n[\n\tsource {}\n\ttarget {}\n\tlabel "{}"\n\t{}\n]\n'
            }        
        body = ""
        gid = ""
        all_nodes = dict()
        node_counter = len(self.groups)
        for group_id, group in enumerate(self.groups):
            if group_id != 0:
                body += formats["group"].format(group_id, 
                    group.label, graphics(group.properties))                
                gid = "gid {}\n".format(group_id)
            for node in group:
                properties = group[node]
                body += formats["node"].format(node_counter, 
                    node, gid, graphics(properties))
                all_nodes[node] = node_counter
                node_counter += 1
        for e in self.edges:
            source, target, label, properties = e
            source_id = all_nodes[source]
            target_id = all_nodes[target]
            body += formats["edge"].format(
                source_id, target_id, label, graphics(properties))
        open(fname+ '.gml', "w"). write(formats["graph"].format(body))
    def tgf(self, fname, include = None, exclude = None):
        body = ""
        all_nodes = dict()
        node_counter = len(self.groups)
        for group in self.groups:
            for node in group:
                if include and node not in include: continue
                if exclude and node in exclude: continue
                body += "{} {}\n".format(node_counter, node)
                all_nodes[node] = node_counter
                node_counter += 1
        body += "#\n"
        for e in self.edges:
            source, target, label, properties = e
            try: 
                source_id = all_nodes[source]
                target_id = all_nodes[target]
            except KeyError:
                continue
            body += "{} {} {}\n".format(source_id, target_id, label)
        open(fname+ '.tgf', "w"). write(body)
    def read_directives(self, text, operators = [], ends = [], assign = []):
        #reads a graph from a sequence of directives
        #each line is of the form: left_hand_side [assign right_hand_side][// comment]
        #right_hand_side is a sequence names interleaved with operators
        operators += ['+', '-', '*', ',', '?', '^', '#', '~', '/', '%', '$']
        ends += [';', "\n"]
        assign += [':=', "="]
        token_separators = chain(operators, ends, assign)
        seps = '|'.join(r'\{}'.format(i) for i in token_separators)
        text = '\n'.join(l[:l.find('\\')] for l in text.splitlines(1))
        dest = None
        side = "LH" # starts from the left hand side
        operator = ""
        tokens = re.split("({})".format(seps), text)
        for s in tokens:
            if s in ends:
                dest = None
                side = "LH"
                continue
            s = s.strip()
            if not s: continue
            if s in assign:
                side = "RH"
            elif s in operators:
                operator = s
            else:
                if side == "LH":
                    dest = s
                    self.add_node(dest)
                else:
                    self.add_node(s)
                    self.add_edge(s, dest, operator)
                    operator = ""
    def fcone(self, *init_set):
        res = set(init_set)
        vol = 0
        while vol != len(res):
            vol = len(res)
            for e in self.edges:
                source, target = e[0], e[1]
                if source in res: 
                    res.add(target)
        return res            
    def bcone(self, *init_set):
        res = set(init_set)
        vol = 0
        while vol != len(res):
            vol = len(res)
            for e in self.edges:
                source, target = e[0], e[1]
                if target in res: 
                    res.add(source)
        return res            
                

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1: 
        if   sys.argv[1] == '-v':
            import doctest
            doctest.testmod()
        elif sys.argv[1] == '-h': 
            print ("Use -v  to run self-test")

