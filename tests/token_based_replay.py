import sys
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.join(current_dir, "..")
sys.path.append(parent_dir)
import pickle
import ocpa.algo.conformance.token_based_replay.algorithm as token_based_replay
from ocpa.objects.log.importer.ocel import factory as ocel_import_factory
import time
from ocpa.algo.discovery.ocpn import algorithm as ocpn_discovery_factory


'''restricted_path=parent_dir+'/sample_logs/ocpn/BPI_restricted_model.pkl'
with open(restricted_path, "rb") as file:
    restrict = pickle.load(file)
flower_path=parent_dir+'/sample_logs/ocpn/BPI_flower.pkl'
with open(flower_path, "rb") as file:
    flower = pickle.load(file)'''

#ocpn_path='./sample_logs/filtered_BPI/BPI_model.pkl'
ocpn_path=current_dir+'/sample_logs/filtered_BPI/BPI_model.pkl'
with open(ocpn_path, "rb") as file:
    ocpn = pickle.load(file)

text_path = current_dir+'/output/test1.txt'
prefix = current_dir+'/sample_logs/filtered_BPI/'
log_list = [(1,2),(2,3),(3,10),(10,50)\
             ,(50,150),(150,550),(550,1550)]

with open(text_path, 'w') as file:
    file.write(f"--------New File--------\n")
path_p2p = '/Users/jiao.shuai.1998.12.01outlook.com/Documents/ocpa/sample_logs/jsonocel/p2p-2023.jsonocel'
path_o2c = '/Users/jiao.shuai.1998.12.01outlook.com/Documents/ocpa/sample_logs/jsonocel/order_process.jsonocel'
path_o2c_2 = '/Users/jiao.shuai.1998.12.01outlook.com/Documents/ocpa/tests/sample_logs/filtered_BPI/o2c.jsonocel'
path_p2p_2 = '/Users/jiao.shuai.1998.12.01outlook.com/Documents/OCEM/sample_logs/jsonocel/p2p-normal.jsonocel'
tf_parameters = {'handle':True,'method':'S_component'}

'''for path in [path_p2p_2,path_o2c_2][:1]:
    ocel = ocel_import_factory.apply(path,parameters={"debug": False})
    cached_parameters = {'BST':False,'activity':True}
    ocpn = ocpn_discovery_factory.apply(ocel, parameters={"debug": False})
    time0= time.time() 
    result = token_based_replay.apply(ocel,ocpn,method='flattened')
    time1= time.time()
    TBR_time = time1-time0 
    with open(text_path, 'a') as file:
        file.write(f"-----Start {path}-----\n\
            evaluation:{result}\n\
            time:{time1-time0}")'''
path = prefix+"BPI1to2executionprocess.jsonocel"
ocel = ocel_import_factory.apply(path,parameters={"debug": False})
ocpn = ocpn_discovery_factory.apply(ocel, parameters={"debug": False})
for ele in log_list[2:7]:
    path = prefix+f"BPI{ele[0]}to{ele[1]}executionprocess.jsonocel"
    ocel = ocel_import_factory.apply(path,parameters={"debug": False})
    #ocpn = ocpn_discovery_factory.apply(ocel, parameters={"debug": False})
    for p in ocpn.places:
        if p.initial:
            print(f'output arcs: {[(a.target.name,a.target.label)for a in p.out_arcs]}')
    cached_parameters = {'BST':False,'activity':True}
    time0= time.time() 
    result = token_based_replay.apply(ocel,ocpn,method='flattened')
    time1= time.time()
    TBR_time = time1-time0 
    out_path_info = current_dir+f"/output/information/info_{ele[0]}to{ele[1]}_log1.pkl"
    with open(text_path, 'a') as file:
        file.write(f"-----Start {path}-----\n\
            evaluation:{result}\n\
            time:{time1-time0}")
    