import numpy as np
import math
import classes.model1 as model1

def make_dict_from_lists(keys, values):
  key_value_pairs = zip(keys, values)
  return dict(key_value_pairs)

#Constants we are going to use
total_weeks = 8
hours_in_week = 24 * 7
hours_in_day = 24
delivery_interval = 7 #days
total_days = 56

#Model sets
tasks = ['T11', 'T12', 'T21', 'T22', 'T31', 'T32', 'T41', 'T42', 'T43', 'T51', 'T52', 'T61', 'T62', 'T63', 'T71', 'T72', 'T81', 'T82', 'T91', 'T92']
units = ['U1', 'U2', 'U3', 'U4', 'U5', 'U6','U7', 'U8', 'U9']
materials = ['RM1', 'RM2', 'INT1', 'INT2', 'INT3', 'INT4', 'INT5', 'A1', 'A2', 'A3', 'A4']
time_points = [i for i in range(total_days + 1)]
time_periods = [i for i in range(1, total_days + 1)]
#Model parameters
capacities = [80, 80, 5, 5, 5, 5, 5, 10, 10, 10, 10] #materials
production_costs = [1.0, 1.0, 0.5, 0.5, 1.5, 1.5, 1.0, 0.5, 0.5, 1.0, 0.5, 0.25, 0.64, 0.19, 0.42, 2.1, 1.2, 0.97, 0.71, 0.55] #tasks
storage_costs = [0, 0, 0, 0, 0, 0, 0, 1.5, 1.4, 1.8, 1.2] #materials
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
  'U6': ['T61', 'T62', 'T63'],
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
  'A1': ['T61', 'T62'],
  'A2': ['T71', 'T72'],
  'A3': ['T81', 'T82'],
  'A4': ['T91', 'T92'],
}

material_consumed_by_tasks = {
  'RM1': ['T21', 'T12', 'T31'],
  'RM2': ['T11', 'T22'],
  'INT1': ['T41', 'T32', 'T42'],
  'INT2': ['T51', 'T43', 'T52'],
  'INT3': ['T61', 'T71'],
  'INT4': ['T62', 'T72', 'T81'],
  'INT5': ['T82', 'T91', 'T92'],
  'A1': [],
  'A2': [],
  'A3': [],
  'A4': []
}

print(time_points)
net_delivery = {}
for k in materials:
  for n in time_points:
    net_delivery[(k,n)] = 0
np.random.seed(42)
rng = np.random.default_rng()
for k in materials[7:]:
  for n in range(delivery_interval, time_points[-1] + 1, delivery_interval):
    net_delivery[(k,n)] = - np.ceil(3 * rng.random())

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
parameters['net_delivery']               = net_delivery
parameters['capacity']                   = capacity
parameters['days_duration']              = 56

model = model1.Model(network, parameters)

vars = model.getVars()
values = model.m.getAttr("X", vars)

result = 'integrality'
for value in vars.values():
  if value != np.ceil(value):
    result = 'not integer'
print(result)