"""Graph related utilities
 A graph is represented by 
    a list of groups and 
    a list of edges
 a group is a dictionary: node_name->properties
 by default, all un-grouped nodes belong to "group" 0
 to add groups, first use add_group
 

"""
import re
from os import listdir, mkdir, remove, chdir, getcwd
from os.path import isdir, join, exists, split, splitext
from itertools import chain
        
class Group(object):
    def __init__(self, group_name, properties = None):
        self.name = group_name
        self.properties = properties
        self.nodes = dict() #node_name -> properties
    def __repr__(self):
        return ', '.join([self.name, str(self.nodes)])
    def __setitem__(self, node_name, properties):
        self.nodes[node_name] = properties
    def __getitem__(self, node_name):
        return self.nodes[node_name]
    def __contains__(self, node_name):
        return (node_name in self.nodes)
    def __iter__(self):
        return iter(self.nodes)
class Graph(object):
    def __init__(self):
        self.groups = [dict()]
        self.edges = []
    def add_group(self, group_name, properties = None):
        self.groups.append(Group(group_name, properties))
    def add_node(self, node_name, group_name = "", properties = None):
        prev_group = self.find_group_id(node_name)#may return None
        group = self.return_group_id(group_name)
        if  prev_group != None:
            prev_properties = self.groups[prev_group].pop(node_name)
            assert not prev_properties or not properties
            assert not prev_group or not group
            group = group or prev_group
            properties = properties or prev_properties
            self.groups[group][node_name] = properties
        else:
            self.groups[group][node_name] = properties 
    def find_group_id(self, node_name):
        for i, group in enumerate(self.groups):
            if node_name in group: return i
    def return_group_id(self, group_name):
        for i, group in enumerate(self.groups):
            if i == 0: continue
            if group_name == group.name: return i
    def add_edge(self, source, target, label = "", properties = None):
        self.edges.append((source, target, label, properties))
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
                    group.name, graphics(group.properties))                
                gid = "gid {}\n".format(group_id)
                all_nodes[group.name] = group_id
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
        operators += ['+', '-', '*', ',', '?', '^', '#', '~', '/', '%', '$', '|', '(']
        ends += [')', ';', '\n']
        assign += [':=', "="]
        token_separators = chain(operators, ends, assign)
        seps = '|'.join(r'\{}'.format(i) for i in token_separators)
        text = '\n'.join(l[:l.find('\\')] for l in text.splitlines(1))
        dest = None
        op1 = None
        op2 = None
        side = "LH" # starts from the left hand side
        operator = ""
        tokens = re.split("({})".format(seps), text)
        for s in tokens:
            if s in ends:
                if op2: 
                    operator, name = op2
                    self.add_node(name)
                    if operator != "(":
                        self.add_edge(name, dest, operator)
                        operator, name = op1
                        self.add_node(name)
                        self.add_edge(name, dest, operator)
                    else:
                        operator, fname = op1
                        self.add_edge(name, dest, operator + fname)
                elif op1:
                    operator, name = op1
                    self.add_node(name)
                    self.add_edge(name, dest, operator)
                dest = None
                op1 = None
                op2 = None
                side = "LH"
                continue
            s = s.strip()
            if not s: continue
            if s in assign:
                side = "RH"
                operator = ""
            elif s in operators:
                assert side == "RH", "No operators allowed in LH side"
                operator = s
            else:
                if side == "LH":
                    dest = s
                    self.add_node(dest)
                else:
                    if not op1: op1 = (operator, s)
                    else: op2 = (operator, s)
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
            print ("Use -v  to run self-test\n","Use -d fname to directives to output.tgf\n")
        elif sys.argv[1] == '-d': 
            Graph().read_directives(open(sys.argv[2]).read()).tgf("output")

