import numpy as np
from classes.model1 import Model1
from classes.model2 import Model2
from classes.model3 import Model3
import pandas as pd
from utils.utils import make_dict_from_lists

np.random.seed(42)

#Constants we are going to use
total_weeks = 8
hours_in_week = 24 * 7
hours_in_day = 24
delivery_interval = 7 #days
total_days = 60
rm_num = 2
intm_num = 5

#Model sets
tasks = ['T11', 'T12', 'T21', 'T22', 'T31', 'T32', 'T41', 'T42', 'T43', 'T51', 'T52', 'T61', 'T62', 'T71', 'T72', 'T81', 'T82', 'T91', 'T92']
units = ['U1', 'U2', 'U3', 'U4', 'U5', 'U6', 'U7', 'U8', 'U9']
materials = ['RM1', 'RM2', 'INT1', 'INT2', 'INT3', 'INT4', 'INT5', 'FP1', 'FP2', 'FP3', 'FP4']
time_points = [i for i in range(total_days + 1)]
time_periods = [i for i in range(1, total_days + 1)]
#Model parameters
capacities = [80, 80, 5, 5, 5, 5, 5, 10, 10, 10, 10] #materials
production_costs = [1.0, 1.0, 0.5, 0.5, 1.5, 1.5, 1.0, 0.5, 0.5, 1.0, 0.5, 0.25, 0.64, 0.19, 0.42, 2.1, 1.2, 0.97, 0.71] #tasks
storage_costs = [0, 0, 0, 0, 0, 0, 0, 1.7, 1.5, 2, 1.6] #materials
onhand_inventory_list = [ 80, 80, 0, 0, 0, 0, 0, 0, 0, 0, 0]

material_storage_cost = make_dict_from_lists(materials, storage_costs)
task_production_cost = make_dict_from_lists(tasks, production_costs)
capacity = make_dict_from_lists(materials, capacities)
onhand_inventory = make_dict_from_lists(materials, onhand_inventory_list)

unit_can_process_tasks = {
  'U1': ['T11', 'T12'],
  'U2': ['T21', 'T22'],
  'U3': ['T31', 'T32'],
  'U4': ['T41', 'T42', 'T43'],
  'U5': ['T51', 'T52'],
  'U6': ['T61', 'T62'],
  'U7': ['T71', 'T72'],
  'U8': ['T81', 'T82'],
  'U9': ['T91', 'T92'],
}

material_produced_by_tasks = {
  'RM1': [],
  'RM2': [],
  'INT1': ['T11', 'T12'],
  'INT2': ['T21', 'T22'],
  'INT3': ['T31', 'T32'],
  'INT4': ['T41', 'T42', 'T43'],
  'INT5': ['T51', 'T52'],
  'FP1': ['T61', 'T62'],
  'FP2': ['T71', 'T72'],
  'FP3': ['T81', 'T82'],
  'FP4': ['T91', 'T92'],
}

material_consumed_by_tasks = {
  'RM1': ['T21', 'T12', 'T31'],
  'RM2': ['T11', 'T22'],
  'INT1': ['T41', 'T32', 'T42'],
  'INT2': ['T51', 'T43', 'T52'],
  'INT3': ['T61', 'T71'],
  'INT4': ['T62', 'T72', 'T81'],
  'INT5': ['T82', 'T91', 'T92'],
  'FP1': [],
  'FP2': [],
  'FP3': [],
  'FP4': []
}

net_delivery_model1 = {}
for k in materials:
  for n in time_points:
    net_delivery_model1[(k,n)] = 0

for k in materials[7:]:
  for n in range(delivery_interval, time_points[-1] + 1, delivery_interval):
    net_delivery_model1[(k,n)] = - np.ceil(3 * np.random.random())
    
net_delivery_model2n3 = {}
for k in materials:
  for n in time_points:
    net_delivery_model2n3[(k,n)] = 0

for k in materials[7:]:
  for n in range(delivery_interval, time_points[-1] + 1, delivery_interval):
    net_delivery_model2n3[(k,n)] = - np.ceil(10 * np.random.random())

network_data = [tasks, materials, units, unit_can_process_tasks, material_consumed_by_tasks, material_produced_by_tasks]
network = {}
network['tasks']                      = tasks
network['materials']                  = materials
network['units']                      = units
network['unit_can_process_tasks']     = unit_can_process_tasks
network['material_consumed_by_tasks'] = material_consumed_by_tasks
network['material_produced_by_tasks'] = material_produced_by_tasks

parameters = {}
parameters['material_storage_cost']      = material_storage_cost
parameters['task_production_cost']       = task_production_cost
parameters['task_daily_production_rate'] = make_dict_from_lists(tasks, [1 for i in range(len(tasks))])
parameters['Dt']                         = 24 
parameters['onhand_inventory']           = onhand_inventory
parameters['capacity']                   = capacity

parameters_model1 = dict(parameters)
parameters_model2n3 = dict(parameters)

parameters_model1['days_duration'] = 56
parameters_model1['net_delivery'] = net_delivery_model1

parameters_model2n3['net_delivery'] = net_delivery_model2n3
parameters_model2n3['days_duration'] = 60
parameters_model2n3['number_of_raw_materials'] = 2
parameters_model2n3['number_of_intermediate_materials'] = 5

model1 = Model1(network, parameters_model1)
model2 = Model2(network, parameters_model2n3)
model3 = Model3(network, parameters_model2n3)

model1.m.optimize()
model2.m.optimize()
model3.m.optimize()

########################## EXPORT DATA ##########################
material_parameters = {'material': materials, 
                       'capacity': capacities,
                       'storage cost': storage_costs,
                       'onhand inventory': onhand_inventory_list
                      }

materials_table = pd.DataFrame(material_parameters)
materials_table.to_csv('data/case2/materials.csv', index=False)

task_parameters = {'task': tasks,
                   'production cost': production_costs 
                  }

tasks_table = pd.DataFrame(task_parameters)
tasks_table.to_csv('data/case2/tasks.csv', index=False)

demand = {}
for material in materials[rm_num + intm_num:]:
  demand[material] = []
  for n in range(delivery_interval, time_points[-1] + 1, delivery_interval):
      demand[material].append(-int(net_delivery_model1[(material, n)]))

demand_table = pd.DataFrame(demand, index=[i for i in range(1, total_weeks + 1)])
demand_table.index.name = 'week'
demand_table.to_csv('data/case2/model1-demand.csv')

demand = {}
for material in materials[rm_num + intm_num:]:
  demand[material] = []
  for n in range(delivery_interval, time_points[-1] + 1, delivery_interval):
      demand[material].append(-int(net_delivery_model2n3[(material, n)]))

demand_table = pd.DataFrame(demand, index=[i for i in range(1, total_weeks + 1)])
demand_table.index.name = 'week'
demand_table.to_csv('data/case2/model2n3-demand.csv')
