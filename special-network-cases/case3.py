from classes.model1 import Model1
from classes.model2 import Model2
from classes.model3 import Model3
from utils.utils import make_dict_from_lists
from utils.utils import calculate_net_delivery
import pandas as pd

#Constants we are going to use
total_weeks = 8
hours_in_week = 24 * 7
hours_in_day = 24
delivery_interval = 7 #days
total_days = 60
rm_num = 2
intm_num = 9
fp_num = 5

#Model sets
tasks = ['T11', 'T12', 'T21', 'T22', 'T31', 'T32', 'T41', 'T51', 'T61', 'T71', 'T81', 'T91', 'T101', 'T111']
units = ['U1', 'U2', 'U3', 'U4', 'U5', 'U6', 'U7', 'U8', 'U9', 'U10', 'U11']
materials = ['RM1', 'RM2', 'INT11', 'INT12', 'INT21', 'INT22', 'INT31', 'INT32', 'INT41', 'INT51', 'INT61', 'FP71', 'FP81', 'FP91', 'FP101', 'FP111']
time_points = [i for i in range(total_days + 1)]
time_periods = [i for i in range(1, total_days + 1)]
#Model parameters
capacities = [80, 80, 5, 5, 5, 5, 5, 5, 5, 5, 5, 10, 10, 10, 10, 10] #materials
production_costs = [1.0, 1.0, 0.5, 0.5, 1.5, 1.5, 1.0, 0.5, 0.5, 1.0, 0.5, 0.25, 0.64, 0.19] #tasks
storage_costs = [0, 0, 0, 0, 0, 0, 1.5, 1.4, 1.8, 1.2, 2.0, 1.75, 1.25, 2.2, 2.3, 5] #materials
onhand_inventory_list = [80, 80, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

material_storage_cost = make_dict_from_lists(materials, storage_costs)
task_production_cost = make_dict_from_lists(tasks, production_costs)
capacity = make_dict_from_lists(materials, capacities)
onhand_inventory = make_dict_from_lists(materials, onhand_inventory_list)

unit_can_process_tasks = {
  'U1': ['T11', 'T12'],
  'U2': ['T21', 'T22'],
  'U3': ['T31', 'T32'],
  'U4': ['T41'],
  'U5': ['T51'],
  'U6': ['T61'],
  'U7': ['T71'],
  'U8': ['T81'],
  'U9': ['T91'],
  'U10': ['T101'],
  'U11': ['T111']
}

material_produced_by_tasks = {
  'RM1': [],
  'RM2': [],
  'INT11': ['T11'],
  'INT12': ['T12'],
  'INT21': ['T21'],
  'INT22': ['T22'],
  'INT31': ['T31'],
  'INT32': ['T32'],
  'INT41': ['T41'],
  'INT51': ['T51'],
  'INT61': ['T61'],
  'INT71': ['T71'],
  'FP71': ['T71'],
  'FP81': ['T81'],
  'FP91': ['T91'],
  'FP101': ['T101'],
  'FP111': ['T111'],
}

material_consumed_by_tasks = {
  'RM1': ['T11', 'T12'],
  'RM2': ['T21', 'T22'],
  'INT11': ['T31', 'T32'],
  'INT12': ['T41'],
  'INT21': ['T71'],
  'INT22': ['T61'],
  'INT31': ['T71'],
  'INT32': ['T91'],
  'INT41': ['T101'],
  'INT51': ['T111'],
  'INT61': ['T81'],
  'FP71': [],
  'FP81': [],
  'FP91': [],
  'FP101': [],
  'FP111': [],
}

net_delivery_model1 = calculate_net_delivery( materials, fp_num, delivery_interval, time_points, ceiling=3 )
net_delivery_model2n3 = calculate_net_delivery( materials, fp_num, delivery_interval, time_points, ceiling=4 )


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
parameters_model1['net_delivery'] = net_delivery_model1
parameters_model1['days_duration']              = 56

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

########################## EXPORT DATA ##########################
material_parameters = {'material': materials, 
                       'capacity': capacities,
                       'storage cost': storage_costs,
                       'onhand inventory': onhand_inventory_list
                      }

materials_table = pd.DataFrame(material_parameters)
materials_table.to_csv('data/case3/materials.csv', index=False)

task_parameters = {'task': tasks,
                   'production cost': production_costs 
                  }

tasks_table = pd.DataFrame(task_parameters)
tasks_table.to_csv('data/case3/tasks.csv', index=False)

demand = {}
for material in materials[rm_num + intm_num:]:
  demand[material] = []
  for n in range(delivery_interval, time_points[-1] + 1, delivery_interval):
      demand[material].append(-int(net_delivery_model1[(material, n)]))

demand_table = pd.DataFrame(demand, index=[i for i in range(1, total_weeks + 1)])
demand_table.index.name = 'week'
demand_table.to_csv('data/case3/model1-demand.csv')

demand = {}
for material in materials[rm_num + intm_num:]:
  demand[material] = []
  for n in range(delivery_interval, time_points[-1] + 1, delivery_interval):
      demand[material].append(-int(net_delivery_model2n3[(material, n)]))

demand_table = pd.DataFrame(demand, index=[i for i in range(1, total_weeks + 1)])
demand_table.index.name = 'week'
demand_table.to_csv('data/case3/model2n3-demand.csv')
