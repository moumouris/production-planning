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
tasks = ['T11', 'T12', 'T21', 'T22', 'T31', 'T32', 'T41', 'T42', 'T43', 'T51', 'T52', 'T61', 'T62', 'T63']
units = ['U1', 'U2', 'U3', 'U4', 'U5', 'U6']
materials = ['RM1', 'RM2', 'INT11', 'INT12', 'INT21', 'INT22', 'INT31', 'INT32', 'INT41', 'INT42', 'INT43', 'FP51', 'FP52', 'FP61', 'FP62', 'FP63']
time_points = [i for i in range(total_days + 1)]
time_periods = [i for i in range(1, total_days + 1)]
#Model parameters
capacities = [80, 80, 5, 5, 5, 5, 5, 5, 5, 5, 5, 10, 10, 10, 10, 10] #materials
production_costs = [1.0, 1.0, 0.5, 0.5, 1.5, 1.5, 1.0, 0.5, 0.5, 1.0, 0.5, 0.25, 0.64, 0.19] #tasks
storage_costs = [0, 0, 0, 0, 0, 0, 1.5, 1.4, 1.8, 1.2, 2.0, 1.75, 1.25, 2.2, 2.3, 5] #materials
onhand_inventory_list = [ 80, 80, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

material_storage_cost = make_dict_from_lists(materials, storage_costs)
task_production_cost = make_dict_from_lists(tasks, production_costs)
capacity = make_dict_from_lists(materials, capacities)
onhand_inventory = make_dict_from_lists(materials, onhand_inventory_list)
print(material_storage_cost)
unit_can_process_tasks = {
  'U1': ['T11', 'T12'],
  'U2': ['T21', 'T22'],
  'U3': ['T31', 'T32'],
  'U4': ['T41'],
  'U5': ['T42'],
  'U6': ['T43'],
  'U7': ['T51'],
  'U8': ['T52'],
  'U9': ['T61'],
  'U10': ['T62'],
  'U11': ['T63']
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
  'INT42': ['T42'],
  'INT43': ['T43'],
  'FP51': ['T51'],
  'FP52': ['T52'],
  'FP61': ['T61'],
  'FP62': ['T62'],
  'FP63': ['T63'],
}

material_consumed_by_tasks = {
  'RM1': ['T11', 'T12'],
  'RM2': ['T21', 'T22'],
  'INT11': ['T31', 'T32'],
  'INT12': ['T41'],
  'INT21': ['T42'],
  'INT22': ['T52'],
  'INT31': ['T51'],
  'INT32': ['T61'],
  'INT41': ['T62'],
  'INT42': ['T63'],
  'INT43': ['T43'],
  'FP51': [],
  'FP52': [],
  'FP61': [],
  'FP62': [],
  'FP63': [],
}

net_delivery = {}
for k in materials:
  for n in time_points:
    net_delivery[(k,n)] = 0

rng = np.random.default_rng()
for k in materials[11:]:
  for n in range(delivery_interval, time_points[-1] + 1, delivery_interval):
    net_delivery[(k,n)] = - np.ceil(2 * rng.random())
print(net_delivery)
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


model.m.optimize()
all_vars = model.m.getVars()
values = model.m.getAttr("X", all_vars)

print(all_vars)
result = 'integrality'
for value in values:
  if value != np.ceil(value):
    result = 'not integer'
print(result)
