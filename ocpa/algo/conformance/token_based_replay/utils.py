from pm4py.objects.petri_net import obj as obj_pm4py
from ocpa.objects.oc_petri_net import obj as obj_ocpa
from ocpa.objects.log.exporter.ocel.factory import apply as ocpa_exporter
import pm4py
from multiset import *

def pn_ocpa2pm4py(pn_ocpa):
    pn_pm4py = {}
    pn_pm4py['object_types']=set()
    pn_pm4py['activities']=set()
    pn_pm4py['petri_nets']={}
    pn_pm4py['object_types'] = set()
    for pl in pn_ocpa.places:
        pn_pm4py['object_types'].add(pl.object_type)
    for ot in list(pn_pm4py['object_types']):
        pn_pm4py['petri_nets'][ot] = []
        pn_pm4py['petri_nets'][ot].append(obj_pm4py.PetriNet())
    s = {}
    t = {}
    for pl in pn_ocpa.places:
        if pl.initial:
            place = obj_pm4py.PetriNet.Place('source')
            s[pl.object_type] = obj_pm4py.Marking()            
            s[pl.object_type][place] = 1
        elif pl.final:
            place = obj_pm4py.PetriNet.Place('sink')
            t[pl.object_type] = obj_pm4py.Marking()     
            t[pl.object_type][place] = 1
        else:
            place = obj_pm4py.PetriNet.Place(pl.name)
        pn_pm4py['petri_nets'][pl.object_type][0].places.add(place)            
    for ot in list(pn_pm4py['object_types']):
        pn_pm4py['petri_nets'][ot].extend([s[ot],t[ot]])
    for tr in pn_ocpa.transitions:
        tran_type = set()
        if not tr.silent:
            pn_pm4py['activities'].add(tr.label)
        for ar in pn_ocpa.arcs:
            if ar.source == tr:
                tran_type.add(ar.target.object_type)
            if ar.target == tr:
                tran_type.add(ar.source.object_type)
        if tr.silent:
            label = None
        else:
            label = tr.label
        for ot in list(tran_type):
            transition = obj_pm4py.PetriNet.Transition(tr.label,label)
            pn_pm4py['petri_nets'][ot][0].transitions.add(transition)
    for ar in pn_ocpa.arcs:
        if type(ar.source)==obj_ocpa.ObjectCentricPetriNet.Place:
            ot = ar.source.object_type
        else:
            ot = ar.target.object_type       
        source = return_correspondence(ar.source,pn_pm4py['petri_nets'][ot][0])
        target = return_correspondence(ar.target,pn_pm4py['petri_nets'][ot][0])
        arcs = obj_pm4py.PetriNet.Arc(source,target,ar.weight,ar.properties)
        pn_pm4py['petri_nets'][ot][0].arcs.add(arcs)           
    for ot in pn_pm4py['object_types']:
        for pl in pn_pm4py['petri_nets'][ot][0].places:
            in_arcs = set()
            out_arcs = set()
            for arc in pn_pm4py['petri_nets'][ot][0].arcs:
                if arc.target == pl:
                    in_arcs.add(arc)
                if arc.source == pl:
                    out_arcs.add(arc)
            pl._Place__in_arcs = in_arcs
            pl._Place__out_arcs = out_arcs
        for tr in pn_pm4py['petri_nets'][ot][0].transitions:
            in_arcs = set()
            out_arcs = set()
            for arc in pn_pm4py['petri_nets'][ot][0].arcs:
                if arc.target == tr:
                    in_arcs.add(arc)
                if arc.source == tr:
                    out_arcs.add(arc)
            tr._Transition__in_arcs = in_arcs
            tr._Transition__out_arcs = out_arcs
    for ot in list(pn_pm4py['object_types']):
        pn_pm4py['petri_nets'][ot]=tuple(pn_pm4py['petri_nets'][ot])
    pn_pm4py['double_arcs_on_activity']={}
    for ot in pn_pm4py['object_types']:
        pn_pm4py['double_arcs_on_activity'][ot]={}
        for act in pn_pm4py['activities']:
            var = False
            for arc in pn_ocpa.arcs:
                if type(arc.source)==obj_pm4py.PetriNet.Transition and arc.source.label == act and arc.variable == True:
                    var = True
                    break
                elif type(arc.target)==obj_pm4py.PetriNet.Transition and arc.target.label == act and arc.variable == True:
                    var = True
                    break
            pn_pm4py['double_arcs_on_activity'][ot][act] = var   
    return pn_pm4py

def return_correspondence(ele,net,ot=None):
    '''
    ------Inputs-------
    ele: the inspected element from ocpa
    net: the object-centric Petri net from pm4py
    ------Output-------
    the correspondence of ele in net
    '''
    if type(ele) == obj_ocpa.ObjectCentricPetriNet.Place:
        if ot != None:
            for pl in net.places:
                if pl.name in ele.name:
                    return pl                 
        if ele.initial:
            for pl in net.places:
                if pl.name == 'source':
                    return pl
        elif ele.final:
            for pl in net.places:
                if pl.name == 'sink':
                    return pl
        else:
            for pl in net.places:
                if pl.name == ele.name:
                    return pl
    elif type(ele) == obj_ocpa.ObjectCentricPetriNet.Transition:
        for tr in net.transitions:
            if tr.name == ele.label:
                return tr

def log_ocpa2pm4py(ocel,export_path='./sample_logs/jsonocel/intermediate.jsonocel'):
    ocpa_exporter(ocel,export_path)
    return pm4py.read_ocel(export_path)