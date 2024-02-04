import gurobipy as gp
from gurobipy import GRB
import numpy as np

import classes.model1 as model1

def make_dict_from_lists(keys, values):
  key_value_pairs = zip(keys, values)
  return dict(key_value_pairs)

#Constants we are going to use
total_weeks = 8
hours_in_week = 24 * 7
hours_in_day = 24
delivery_interval = 7 #days
Dt = 12 #hours

#Model sets
tasks = ['T11', 'T12', 'T21', 'T22', 'T31', 'T32', 'T41', 'T42', 'T43', 'T51', 'T52']
units = ['U1', 'U2', 'U3', 'U4', 'U5']
materials = ['RM1', 'RM2', 'INT1', 'INT2', 'INT3', 'INT4', 'A', 'B1', 'B2', 'C1', 'C2']
time_points = [i for i in range(int(56 * 24 / Dt) + 1)]
time_periods = [i for i in range(1, int(56 * 24 / Dt) + 1)]

#Model parameters
capacities = [80, 80, 5, 5, 5, 5, 10, 10, 10, 10, 10] #materials
production_costs = [1.0, 1.0, 0.5, 0.5, 1.5, 1.5, 1.0, 0.5, 0.5, 1.0, 0.5] #tasks
storage_costs = [0, 0, 0, 0, 0, 0, 1.5, 1.4, 1.8, 1.2, 2.0] #materials
daily_production_rate = [2, 1, 1, 1, 2, 2, 2, 1, 1, 1, 1] #tasks
onhand_inventory_list = [ 80, 80, 0, 0, 0, 0, 0, 0, 0, 0, 0]

material_storage_cost = make_dict_from_lists(materials, storage_costs)
task_production_cost = make_dict_from_lists(tasks, production_costs)
capacity = make_dict_from_lists(materials, capacities)
task_daily_production_rate = make_dict_from_lists(tasks, daily_production_rate)
onhand_inventory = make_dict_from_lists(materials, onhand_inventory_list)

unit_can_process_tasks = {
  'U1': ['T11', 'T12'],
  'U2': ['T21', 'T22'],
  'U3': ['T31', 'T32'],
  'U4': ['T41', 'T42', 'T43'],
  'U5': ['T51', 'T52']
}

material_produced_by_tasks = {
  'RM1': [],
  'RM2': [],
  'INT1': ['T11', 'T21'],
  'INT2': ['T12', 'T22'],
  'INT3': ['T31'],
  'INT4': ['T32'],
  'A': ['T41'],
  'B1': ['T42'],
  'B2': ['T51'],
  'C1': ['T43'],
  'C2': ['T52']
}

material_consumed_by_tasks = {
  'RM1': ['T11', 'T21'],
  'RM2': ['T12', 'T22'],
  'INT1': ['T31', 'T41'],
  'INT2': ['T32'],
  'INT3': ['T42', 'T51'],
  'INT4': ['T43', 'T52'],
  'A': [],
  'B1': [],
  'B2': [],
  'C1': [],
  'C2': []
}

net_delivery = {}
for k in materials:
  for n in time_points:
    net_delivery[(k,n)] = 0

fp_deliveries_string = "3.0 2.5 3.5 2.5 2.5\
                        3.5 3.0 3.0 2.0 3.5\
                        2.5 2.5 2.5 1.0 1.5\
                        3.0 2.0 3.0 2.0 3.0\
                        1.5 2.0 1.5 0.5 3.0\
                        2.5 3.0 3.0 2.5 2.0\
                        4.0 0.0 1.0 2.0 1.5\
                        3.0 2.5 2.5 2.0 1.5"

fp_deliveries = np.array([-float(x) for x in fp_deliveries_string.split()])
fp_deliveries = fp_deliveries.reshape(8, 5)

for i, k in enumerate(materials[6:]):
  for j, n in enumerate(range(int(delivery_interval * (24 / Dt)), time_points[-1] + 1, int(delivery_interval * (24 / Dt)))):
    net_delivery[(k,n)] = fp_deliveries[j][i]

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
parameters['task_daily_production_rate'] = task_daily_production_rate
parameters['Dt']                         = Dt
parameters['onhand_inventory']           = onhand_inventory
parameters['net_delivery']               = net_delivery
parameters['capacity']                   = capacity
parameters['days_duration']              = 56

model = model1.Model1(network, parameters)
model.m.optimize()