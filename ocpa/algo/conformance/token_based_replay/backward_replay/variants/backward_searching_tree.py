from ocpa.objects.oc_petri_net import obj as obj_ocpa
from multiset import *
import copy

def extend_bst(bst,node):
    place = node.place
    object_type = place.object_type
    ingoing_silence_list = [arc.source for arc in place.in_arcs if arc.source.silent]
    if len(ingoing_silence_list) == 0:
        node.color = 'red'
    else:
        if len(ingoing_silence_list) > 1:
            operator1 = bst.Operator(len(bst.operators),'OR')
            is_OR = True
        else:
            operator1 = bst.Operator(len(bst.operators),type='AND',transition=ingoing_silence_list[0])
            is_OR = False
        bst.connect_components(operator1,node)
        bst.operators.add(operator1)
        for silence in ingoing_silence_list:
            preset = [arc for arc in silence.in_arcs if arc.source.object_type == object_type]
            if len(preset) == 0:
                return ValueError(f'the silence {silence} has no preset of object type {object_type}')
            elif len(preset) == 1:
                pl = list(silence.in_arcs)[0].source
                if is_OR:
                    transition = silence
                else:
                    transition = None
                parent_operator = operator1
            elif len(preset) > 1:
                if is_OR:
                    operator2 = bst.Operator(len(bst.operators),'AND',transition=silence)
                    bst.connect_components(operator2,operator1)
                    bst.operators.add(operator2)
                    parent_operator = operator2                   
                else:
                    parent_operator = operator1
                transition = None                    
            for arc in preset:
                state = bst.Node(len(bst.nodes),place=arc.source,transition=transition,end=True,weight=arc.weight)
                bst.connect_components(state,parent_operator)
                bst.nodes.add(state)

class BackwardSearchingTree(object):
    def __init__(self):
        self.nodes = set()
        self.operators = set()
        self.root = None
        self.constrains = {}
    class Node(object):
        def __init__(self,name,place,transition=None,label=None,end=False,weight=1):
            self.id = 'node'+str(id)
            self.name = place.name
            self.place = place
            self.transition = transition
            self.label = transition.label if not transition is None else label
            self.parent = None
            self.children = set()
            self.color = 'yellow'
            self.visit = []
            self.weight=weight
            self.end = end
        def __repr__(self) -> str:
            return self.id
        def __eq__(self, other):
            return id(self) == id(other)
        def __hash__(self):
            return id(self) 
    class Operator(object):
        def __init__(self,id,type,transition=None,label=None):
            self.id = 'operator'+str(id)
            self.type = type
            self.transition = transition
            self.label = transition.label if not transition is None else label
            self.parent = None
            self.children = set()
            self.color = 'yellow'
            self.visit = []
            self.end = False
        def __repr__(self) -> str:
            return self.id
        def __eq__(self, other):
            return id(self) == id(other)
        def __hash__(self):
            return id(self)
    def connect_components(self,parent,child):
        parent.parent = child
        child.children.add(parent)
        parent.end = True
        child.end = False
        parent.visit = copy.deepcopy(child.visit)
        if type(parent) == BackwardSearchingTree.Node:
            parent.visit.insert(0,parent.label)

    def prune_color(self,element):
        if type(element) == self.Node:
            for n in element.children:
                self.prune_color(n)
                n.color = 'grey'
        elif type(element) == self.Operator:           
            for n in element.children:
                if n.color == 'yellow':
                    self.prune_color(n)
                    n.color = 'grey'

    @property
    def extension_nodes(self):
        return [n for n in self.nodes if n.end and n.color=='yellow']
    
    @property
    def all_green(self):
        return all([o.color=='green' for o in self.operators])
    
    @property
    def any_red(self):
        return any([o.color=='red' for o in self.operators])
    
    
    def color_update(self):        
        no_update = False
        while not no_update:
            no_update = True
            #FIFO
            operator_list = sorted(self.operators, key=lambda x: len(x.visit))
            node_list = sorted(self.nodes,key=lambda x:len(x.visit))  
            for o in operator_list:
                if o.type == 'AND' and o.color == 'yellow':
                    if all([n.color == 'green' for n in o.children]):
                        o.color = 'green'
                        if o in self.constrains.keys():
                            for conseq in self.constrains[o]:
                                conseq.color = 'green'
                        no_update = False
                    elif any([n.color == 'red' for n in o.children]):
                        o.color = 'red'
                        no_update = False
                        self.prune_color(o)
                elif o.type == 'OR' and o.color == 'yellow':
                    if all([n.color == 'red' for n in o.children]):
                        o.color = 'red'
                        no_update = False
                    elif any([n.color == 'green' for n in o.children]):
                        o.color = 'green'
                        if o in self.constrains.keys():
                            for conseq in self.constrains[o]:
                                conseq.color = 'green'
                        no_update = False
                        self.prune_color(o)
            for n in node_list:    
                if len(n.children) == 1 and n.color == 'yellow':
                    o = list(n.children)[0]
                    if o.color == 'green' and not o.end:
                        n.color = 'green'
                        if n in self.constrains.keys():
                            for conseq in self.constrains[n]:
                                conseq.color = 'green'
                        no_update = False
                    elif o.color == 'red' and not o.end:
                        n.color = 'red'
                        no_update = False

    def extract_silence_sequence(self):
        silence_sequence = []
        for n in self.root.children:
            if n.color == 'green':
                silence_sequence = self.get_path_above(n) + silence_sequence
        return silence_sequence                         

    def get_bst_label(self):
        return ['node: ']+[(n.label,n.end,n.color) for n in self.nodes]+[', operator: ']+[(o.label,o.type,o.color) for o in self.operators]
    
    def get_path_above(self,ele):
        if type(ele) == self.Node:           
            if ele.end and ele.color == 'green':
                return [ele.transition]
            elif ele.color == 'green':
                if len(ele.children) > 1:
                    return ValueError(f'node {ele} has multiple children')
                return self.get_path_above(list(ele.children)[0])+[ele.transition]
            elif ele.color == 'red':
                return []
        elif type(ele) == self.Operator:
            if ele.type == 'AND' and ele.color == 'green':
                and_join_path = [ele.transition]
                for child in ele.children:
                    and_join_path = self.get_path_above(child)+ and_join_path
                return and_join_path
            if ele.type == 'OR' and ele.color == 'green':                    
                for child in ele.children:
                    if child.color == 'green':
                        or_join_path = self.get_path_above(child)
                        break
                return or_join_path
            if ele.color == 'red':
                return []
    
    def get_missing_nodes(self):
        missing_places = []
        for n in self.root.children:
            if not n.color == 'green':
                missing_places.append((n.place,n.weight))
        return missing_places
    
    def is_place_occupied(self,pl):
        for n in self.nodes:
            if n.place == pl and n.end and n.color == 'green':
                return True
        return False

def get_bst_information(bst):
    depth_list,breadth_list,num_nodes_list = [],[],[]
    num_trees = 0
    for tree in bst.values():
        tree_depth = []
        breadth = 0
        num_nodes = 0
        num_trees += 1
        for n in tree.nodes: 
            num_nodes += 1           
            if n.end:
                breadth += 1
                depth = 0
                current = n
                while not current == tree.root:
                    current = current.parent
                    depth += 1
                tree_depth.append(depth)
        depth_list.append(max(tree_depth))
        breadth_list.append(breadth)
        num_nodes_list.append(num_nodes)
    return {'deepth':depth_list,'breadth':breadth_list,'number_of_nodes':num_nodes_list,'number_of_BST':num_trees}

def calculate_silence_constrain(ocpn):
    silence_constrain = {}
    for tr in ocpn.transitions:
        if tr.silent and len(tr.out_arcs)>1:
            silence_constrain[tr] = set([a.target for a in tr.out_arcs])
    return silence_constrain


def calculate_bst_constrain(bst,silence_constrain):
    bst_constrain = {}
    for ele in bst.nodes|bst.operators:
        if ele.transition in silence_constrain.keys():
            bst_constrain[ele] = set()
            for pl in silence_constrain[ele.transition]:
                for n in bst.nodes:
                    if n.place == pl:
                        bst_constrain[ele].add(n)  
    return bst_constrain

def caching_bst(ocpn):    
    backward_transitions = [(tr,ot) for tr in ocpn.transitions for ot in ocpn.object_types if any([a2.source.silent for a1 in tr.in_arcs if a1.source.object_type==ot for a2 in a1.source.in_arcs]) and not tr.silent]
    backward_places = [(pl,pl.object_type) for pl in ocpn.places if pl.final]
    backward_elements = backward_transitions + backward_places
    bst_dict = {}
    for (ele,ot) in backward_elements:
            bst = BackwardSearchingTree()
            if type(ele) == obj_ocpa.ObjectCentricPetriNet.Transition:                   
                bst.root = bst.Operator(len(bst.operators),type='AND',transition=ele)           
                bst.operators.add(bst.root)
                preset = [(arc.source,arc.weight) for arc in ele.in_arcs if arc.source.object_type==ot]        
                for (pl,w) in preset:
                    node = bst.Node(len(bst.nodes),place=pl,transition=None,end=True,weight=w)
                    bst.nodes.add(node)
                    bst.connect_components(node,bst.root)
            elif type(ele) == obj_ocpa.ObjectCentricPetriNet.Place:   
                bst.root = bst.Operator(len(bst.operators),type='AND',label='dummy')
                node = bst.Node(len(bst.nodes),place=ele,transition=None,end=True,weight=1)
                bst.connect_components(node,bst.root)
                bst.operators.add(bst.root)
                bst.nodes.add(node)
            while bst.extension_nodes:               
                for n in bst.extension_nodes:
                    if n.label in n.parent.visit and not n.label is None:
                        n.color = 'red'
                    else:
                        extend_bst(bst,n)
            for n in bst.nodes:
                n.color = 'yellow'
                if not n.children:
                    n.end = True
            bst_dict[(ele,ot)] = bst
    return bst_dict
