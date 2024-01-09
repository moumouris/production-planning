import numpy as np
from classes.model1 import Model1
from classes.model2 import Model2
from classes.model3 import Model3
import pandas as pd
from utils import utils

np.random.seed(42)

#Constants we are going to use
total_weeks = 8
hours_in_week = 24 * 7
hours_in_day = 24
delivery_interval = 7 #days
total_days = 60
rm_num = 2
intm_num = 4
fp_num = 5

#Model sets
tasks = ['T11', 'T12', 'T21', 'T22', 'T31', 'T32', 'T41', 'T42', 'T43', 'T51', 'T52', 'T61', 'T62', 'T63']
units = ['U11', 'U12', 'U23', 'U24', 'U35', 'U36']
materials = ['RM1', 'RM2', 'INT1', 'INT2', 'INT3', 'INT4', 'FP1', 'FP2', 'FP3', 'FP4', 'FP5']
time_points = [i for i in range(total_days + 1)]
time_periods = [i for i in range(1, total_days + 1)]
#Model parameters
capacities = [80, 80, 5, 5, 5, 5, 10, 10, 10, 10, 10] #materials
production_costs = [1.0, 1.0, 0.5, 0.5, 1.5, 1.5, 1.0, 0.5, 0.5, 1.0, 0.5, 0.25, 0.64, 0.19] #tasks
storage_costs = [0, 0, 0, 0, 0, 0, 1.5, 1.4, 1.8, 1.2, 2.0] #materials
onhand_inventory_list = [ 80, 80, 0, 0, 0, 0, 0, 0, 0, 0, 0]

material_storage_cost = utils.make_dict_from_lists(materials, storage_costs)
task_production_cost = utils.make_dict_from_lists(tasks, production_costs)
capacity = utils.make_dict_from_lists(materials, capacities)
onhand_inventory = utils.make_dict_from_lists(materials, onhand_inventory_list)

unit_can_process_tasks = {
  'U11': ['T11', 'T12'],
  'U12': ['T21', 'T22'],
  'U23': ['T31', 'T32'],
  'U24': ['T41', 'T42', 'T43'],
  'U35': ['T51', 'T52'],
  'U36': ['T61', 'T62', 'T63']
}

material_produced_by_tasks = {
  'RM1': [],
  'RM2': [],
  'INT1': ['T11', 'T21'],
  'INT2': ['T12', 'T22'],
  'INT3': ['T31', 'T32', 'T41'],
  'INT4': ['T42', 'T43'],
  'FP1': ['T51'],
  'FP2': ['T52'],
  'FP3': ['T61'],
  'FP4': ['T62'],
  'FP5': ['T63']
}

material_consumed_by_tasks = {
  'RM1': ['T11', 'T12'],
  'RM2': ['T21', 'T22'],
  'INT1': ['T31', 'T32'],
  'INT2': ['T41', 'T42', 'T43'],
  'INT3': ['T51', 'T52'],
  'INT4': ['T61', 'T62', 'T63'],
  'FP1': [],
  'FP2': [],
  'FP3': [],
  'FP4': [],
  'FP5': []
}

net_delivery_model1 = {}
for k in materials:
  for n in time_points:
    net_delivery_model1[(k,n)] = 0

for k in materials[6:]:
  for n in range(delivery_interval, time_points[-1] + 1, delivery_interval):
    net_delivery_model1[(k,n)] = - np.ceil(3 * np.random.random())

net_delivery_model2n3 = {}
for k in materials:
  for n in time_points:
    net_delivery_model2n3[(k,n)] = 0

for k in materials[6:]:
  for n in range(delivery_interval, time_points[-1] + 1, delivery_interval):
    net_delivery_model2n3[(k,n)] = - np.ceil(4 * np.random.random())

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
parameters['task_daily_production_rate'] = utils.make_dict_from_lists(tasks, [1 for i in range(len(tasks))])
parameters['Dt']                         = 24 
parameters['onhand_inventory']           = onhand_inventory
parameters['capacity']                   = capacity

parameters_model1 = dict(parameters)
parameters_model1['days_duration'] = 56
parameters_model1['net_delivery'] = net_delivery_model1

parameters_model2n3 = dict(parameters)
parameters_model2n3['net_delivery'] = net_delivery_model2n3
parameters_model2n3['number_of_raw_materials']          = 2
parameters_model2n3['number_of_intermediate_materials'] = 4
parameters_model2n3['days_duration'] = 60

model1 = Model1(network, parameters_model1)
model2 = Model2(network, parameters_model2n3)
model3 = Model3(network, parameters_model2n3)

model1.m.optimize()
model2.m.optimize()
model3.m.optimize()

#################### EXPORT DATA ##############################
material_parameters = {'material': materials, 
                       'capacity': capacities,
                       'storage cost': storage_costs,
                       'onhand inventory': onhand_inventory_list
                      }
materials_table = pd.DataFrame(material_parameters)
materials_table.to_csv('data/case1/materials.csv', index=False)

task_parameters = {'task': tasks,
                   'production cost': production_costs 
                  }

tasks_table = pd.DataFrame(task_parameters)
tasks_table.to_csv('data/case1/tasks.csv', index=False)

demand = {}
for material in materials[rm_num + intm_num:]:
  demand[material] = []
  for n in range(delivery_interval, time_points[-1] + 1, delivery_interval):
      demand[material].append( -int(net_delivery_model1[(material, n)]))

demand_table = pd.DataFrame(demand, index=[i for i in range(1, total_weeks + 1)])
demand_table.index.name = 'week'
demand_table.to_csv('data/case1/model1-demand.csv')

demand = {}
for material in materials[rm_num + intm_num:]:
  demand[material] = []
  for n in range(delivery_interval, time_points[-1] + 1, delivery_interval):
      demand[material].append( -int(net_delivery_model2n3[(material, n)]))

demand_table = pd.DataFrame(demand, index=[i for i in range(1, total_weeks + 1)])
demand_table.index.name = 'week'
demand_table.to_csv('data/case1/model2n3-demand.csv')