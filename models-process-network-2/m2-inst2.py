import gurobipy as gp
from gurobipy import GRB
import numpy as np
from classes.model2 import Model2
from utils.utils import make_dict_from_lists

Dt = 4 #hours
n = 60 #days 
fp_delivery_interval = 7 #days
rm_delivery_interval = 14 #days
rm_num = 3
intm_num = 13
fp_num = 12
tasks_string  = "T111 T112 T121 T122 T123 T131 T132 T211 T212 T213 T214 T221 T222 T223 T224 T311 T312 T321 T322 T331 T332 T411 T412 T413 T414\
        T421 T422 T423 T424 T431 T432 T433 T434 T441 T442 T443 T444"
materials_string = "RM1 RM2 RM3 IN1A IN1B IN1CD IN2A IN2B IN2C IN2D IN3A1 IN3B1 IN3A2 IN3B2 IN3C IN3D A11 \
  B11 A21 B21 A12 B12 A22 B22 C1 D1 C2 D2"

tasks = tasks_string.split()
materials = materials_string.split()
units = ['U11', 'U12', 'U13', 'U21', 'U22', 'U31', 'U32', 'U33', 'U41', 'U42', 'U43', 'U44']
time_points = [i for i in range(int(n * (24 / Dt)) + 1)]

time_periods = [i for i in range(1, int(n * (24 / Dt)) + 1)]
capacities_string = "80.0 80.0 80.0 5.0 5.0 5.0 3.5 3.5 3.5 3.5 3.0 3.0 3.0 3.0 3.0 3.0 10.0 10.0 10.0 10.0 10.0 10.0 10.0 10.0 10.0 10.0 10.0 10.0"
onhand_inventory_string = "35.0 50.0 40.0 3.0 3.0 3.0 1.0 1.0 1.0 1.0 1.0 1.0 1.0 1.5 1.5 1.5 3.0 3.0 3.0 3.0 2.0 2.0 2.0 2.0 3.0 3.0 3.0 3.0"
production_costs_string = "1.50 3.00 2.50 2.00 2.00 1.50 2.00 3.00 1.50 2.50 3.00 2.50 3.00 3.00 1.50 2.50 1.50 2.00 2.50 2.00 2.00 2.00 1.50 1.50 2.50 3.00 1.50 2.50 3.00 2.00 1.50 2.50 1.50 3.00 2.00 2.00 2.50"
daily_production_rate_string = "1.50 1.50 1.00 1.00 1.00 1.00 1.00 1.50 1.50 1.50 1.50 1.50 1.50 1.50 1.50 1.00 1.00 1.50 1.50 1.50 1.50 1.00 1.00 1.00 1.00 0.50 0.50 0.50 0.50 0.75 0.75 0.75 0.75 1.00 1.00 1.00 1.00"

capacities = [float(x) for x in capacities_string.split(' ')]
onhand_inventory = [float(x) for x in onhand_inventory_string.split(' ')]
production_costs = [float(x) for x in production_costs_string.split(' ')]
daily_production_rate = [float(x) for x in daily_production_rate_string.split(' ')]
production_rate = [rate * (Dt / 24) for rate in daily_production_rate]
storage_costs = [0 for i in range(16)] + [0.3, 0.5, 0.4, 0.8, 0.6, 0.6, 0.5, 0.8, 0.8, 1.2, 1, 1.5]

key_value_pairs_storage_cost = zip(materials, storage_costs)
key_value_pairs_production_cost = zip(tasks, production_costs)
key_value_pairs_capacity = zip(materials, capacities)
key_value_pairs_production_rate = zip(tasks, production_rate)
key_value_pairs_onhand_inventory = zip(materials, onhand_inventory)

material_storage_cost = dict(key_value_pairs_storage_cost)
task_production_cost = dict(key_value_pairs_production_cost)
capacity = dict(key_value_pairs_capacity)
rate = dict(key_value_pairs_production_rate)
onhand_inventory = dict(key_value_pairs_onhand_inventory)
rm_deliveries = {
  'RM1': [6.50, 7.00, 6.00],
  'RM2': [7.50, 10.00, 6.50],
  'RM3': [6.50, 10.50, 8.50]
}

fp_deliveries_string = "2.00 3.00 3.50 3.00 1.50 1.00 1.00 3.00 2.50 1.00 3.50 1.00\
 1.50 2.50 3.50 1.50 1.00 3.00 3.00 2.00 2.00 1.50 1.50 1.00\
 4.00 2.00 3.50 2.00 1.00 3.50 1.00 1.50 1.00 1.50 2.50 1.50\
 1.50 2.00 2.00 2.00 4.00 4.00 2.00 2.00 3.50 2.00 4.00 1.00\
 3.50 1.00 3.00 1.00 1.00 2.00 2.50 3.00 1.50 2.00 1.50 1.50\
 4.00 2.00 1.00 2.00 2.00 1.50 4.00 1.50 2.00 1.00 2.00 1.00\
 2.00 2.00 1.50 1.00 3.00 2.50 1.00 3.50 4.00 3.00 3.00 2.00\
 3.00 3.00 2.50 1.50 3.00 2.50 1.00 4.00 1.50 3.00 3.50 4.00"

fp_deliveries = np.array([-float(x) for x in fp_deliveries_string.split()])
fp_deliveries = fp_deliveries.reshape(8, 12)
net_delivery = {}

for k in materials:
  for n in time_points[1:]:
    net_delivery[(k,n)] = 0

#net_delivery for final products
for i, k in enumerate(materials[16:]):
  for j, n in enumerate(range(int(fp_delivery_interval * (24 / Dt)), time_points[-1], int(fp_delivery_interval * (24 / Dt)))):
    net_delivery[(k,n)] = fp_deliveries[j][i]

#net_delivery for raw materials
for k in materials[:rm_num]:
  for i,n in enumerate(range(int(rm_delivery_interval * (24 / Dt) ), time_points[int(rm_delivery_interval * (24 / Dt) ) * 3 + 1], int(rm_delivery_interval * (24 / Dt) ))):
    net_delivery[(k,n)] = rm_deliveries[k][i]

unit_can_process_tasks = {}
for unit in units:
    unit_list = []
    for task in tasks:
        if(unit[1:] == task[1:3]):
            unit_list.append(task)
        elif(len(unit_list)):
            break
    unit_can_process_tasks[unit] = unit_list

materials_produced_by_tasks = {
  'RM1': [],
  'RM2': [],
  'RM3': [],
  'IN1A': ['T111', 'T121'],
  'IN1B': ['T112', 'T122', 'T131'],
  'IN1CD': ['T123', 'T132'],
  'IN2A': ['T211', 'T221'],
  'IN2B': ['T212', 'T222'],
  'IN2C': ['T213', 'T223'],
  'IN2D': ['T214', 'T224'],
  'IN3A1': ['T311'],
  'IN3B1': ['T312'],
  'IN3A2': ['T321'],
  'IN3B2': ['T322'],
  'IN3C': ['T331'],
  'IN3D': ['T332'],
  'A11': ['T411'],
  'B11': ['T412'],
  'A21': ['T413'],
  'B21': ['T414'],
  'A12': ['T421', 'T431'],
  'B12': ['T422', 'T432'],
  'A22': ['T422', 'T433'],
  'B22': ['T424', 'T434'],
  'C1': ['T441'],
  'D1': ['T442'],
  'C2': ['T443'],
  'D2': ['T444']
}

materials_consumed_by_tasks =  {
  'RM1': ['T111', 'T121'],
  'RM2': ['T112', 'T122', 'T131'],
  'RM3': ['T123', 'T132'],
  'IN1A': ['T211', 'T221'],
  'IN1B': ['T212', 'T222'],
  'IN1CD': ['T213', 'T214', 'T223', 'T224'],
  'IN2A': ['T311', 'T321'],
  'IN2B': ['T312', 'T322'],
  'IN2C': ['T331'],
  'IN2D': ['T332'],
  'IN3A1': ['T411', 'T421', 'T431'],
  'IN3B1': ['T412', 'T422', 'T432'],
  'IN3A2': ['T413', 'T423', 'T433'],
  'IN3B2': ['T414', 'T424', 'T434'],
  'IN3C': ['T441', 'T442'],
  'IN3D': ['T443', 'T444'],
  'A11': [],
  'B11': [],
  'A21': [],
  'B21': [],
  'A12': [],
  'B12': [],
  'A22': [],
  'B22': [],
  'C1': [],
  'D1': [],
  'C2': [],
  'D2': []
  } 
  
network = {}
network['tasks']                      = tasks
network['materials']                  = materials
network['units']                      = units
network['unit_can_process_tasks']     = unit_can_process_tasks
network['material_consumed_by_tasks'] = materials_consumed_by_tasks
network['material_produced_by_tasks'] = materials_produced_by_tasks

parameters = {}
parameters['material_storage_cost']      = material_storage_cost
parameters['task_production_cost']       = task_production_cost
parameters['task_daily_production_rate'] = make_dict_from_lists(tasks, daily_production_rate)
parameters['Dt']                         = Dt
parameters['onhand_inventory']           = onhand_inventory
parameters['net_delivery']               = net_delivery
parameters['capacity']                   = capacity
parameters['days_duration']                    = 60
parameters['number_of_raw_materials']          = rm_num
parameters['number_of_intermediate_materials'] = intm_num

time_limit_for_gurobi = 600

model = Model2(network, parameters)
model.m.setParam('timeLimit', time_limit_for_gurobi)
model.m.optimize()
model.m.write('test1.lp')

