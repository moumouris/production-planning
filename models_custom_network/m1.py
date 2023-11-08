import pickle
import random
import math
import gurobipy as gp
from gurobipy import GRB
random.seed(42)
with open("../custom_process_network/custom_process_network.pkl", "rb") as file:
    process_network = pickle.load(file)
with open("../custom_process_network/unit_can_process_tasks.pkl", "rb") as file:
    unit_can_process_tasks = pickle.load(file)
with open("../custom_process_network/materials_for_each_type.pkl", "rb") as file:
    materials_for_each_type = pickle.load(file)

network_nodes = process_network.nodes(data=True)
tasks = [node for node, data in network_nodes if data.get('node_type') == 'tasks']
materials = [node for node, data in network_nodes if data.get('node_type') == 'materials']

material_produced_by_tasks = {}
material_consumed_by_tasks = {}
for material in materials:
   material_produced_by_tasks[material] = list(process_network.predecessors(material))
   material_consumed_by_tasks[material] = list(process_network.successors(material))
   
Dt = 4
weeks = 8
days = 56
capacities_per_material_type = {
   'RM': 90,
   'INA': 4,
   'INB': 5,
   'INC': 4,
   'FP': 12,
}

#Generate capacities
capacities = {}
for material_type in materials_for_each_type:
   for material in materials_for_each_type[material_type]:
      capacities[material] = capacities_per_material_type[material_type]


task_possible_production_costs = [1.5, 2, 1, 3]
task_production_costs = {}
for task in tasks:
   task_production_costs[task] = random.choice(task_possible_production_costs)


#Generate storage costs
storage_costs = {}
possible_storage_costs_for_final_products = [float(i)/10 for i in range(1, 15) ]
for material_type in materials_for_each_type:
   for material in materials_for_each_type[material_type]:
      if material_type == 'FP':
         storage_costs[material] = random.choice(possible_storage_costs_for_final_products)
      else:
         storage_costs[material] = 0

#Generate daily production rates
task_possible_daily_production_rates = [1, 2, 1, 3]
task_daily_production_rates = {}
task_production_rates = {}
for task in tasks:
   task_daily_production_rates[task] = random.choice(task_possible_daily_production_rates)
   task_production_rates[task] = task_daily_production_rates[task] * (Dt /24)

#Generate onhand inventory
onhand_inventory = {}
for material_type in materials_for_each_type:
   for material in materials_for_each_type[material_type]:
      if material_type == 'RM':
         onhand_inventory[material] = 80
      else:
         onhand_inventory[material] = 0


time_points = [i for i in range(int(days * (24 / Dt)) + 1)]

#Generate net delivery
net_delivery = {}
for k in materials:
  for n in time_points[1:]:
    net_delivery[(k,n)] = 0

fp_delivery_interval = 7
rm_delivery_interval = 14
#net_delivery for final products
for i, k in enumerate(materials[-12:]):
  for j, n in enumerate(range(int(fp_delivery_interval * (24 / Dt)), time_points[-1] + 1, int(fp_delivery_interval * (24 / Dt)))):
    net_delivery[(k,n)] = - random.choice([1, 2, 3])

#net_delivery for raw materials
for k in materials[:4]:
  for i,n in enumerate(range(int(rm_delivery_interval * (24 / Dt) ), time_points[int(rm_delivery_interval * (24 / Dt) ) * 3 + 1], int(rm_delivery_interval * (24 / Dt) ))):
    net_delivery[(k,n)] = random.choice([4, 6, 8, 10, 12])


time_periods = [i for i in range(1, int(weeks * 24 * 7 / Dt) + 1)]

units = list(unit_can_process_tasks.keys())

#Here goes the model
m = gp.Model("production-planning-simple")
#Define model variables
w = m.addVars(tasks, time_periods, vtype=GRB.BINARY, name="w")
w_s = m.addVars(units, time_periods, vtype=GRB.BINARY, name="w_s")

s = m.addVars(materials, time_points[1:], vtype=GRB.CONTINUOUS, lb=0, name="s")
#Define objective function
obj = sum( storage_costs[k] * Dt / 24 * s[k,n] for k in materials for n in time_points[1:]) + \
      sum(task_production_costs[i] * task_production_rates[i] * w[i,n] for n in time_periods for i in tasks)

m.setObjective(obj, GRB.MINIMIZE)
#Define constraints
capacity_constraint = m.addConstrs(s[k,n] <= capacities[k] for k in materials for n in time_points[1:])

assignment = m.addConstrs(sum(w[i,n] for i in unit_can_process_tasks[j]) + w_s[j,n] == 1 \
  for j in units for n in time_periods)

initial_balance = m.addConstrs(s[k,1] == onhand_inventory[k] + net_delivery[k,1] \
  + sum(task_production_rates[i] * w[i,1] for i in material_produced_by_tasks[k]) \
  - sum(task_production_rates[i] * w[i,1] for i in material_consumed_by_tasks[k]) \
                             for k in materials )
                             
balance = m.addConstrs(s[k,n] == s[k,n-1] + net_delivery[k,n] \
  + sum(task_production_rates[i] * w[i,n] for i in material_produced_by_tasks[k]) \
  - sum(task_production_rates[i] * w[i,n] for i in material_consumed_by_tasks[k]) \
  for k in materials for n in time_points[2:] )
            
m.write( 'test.lp' )

m.optimize()

# #check that every task produces/consumes one and only one material
# #to be a function
# merged_list = [item for sublist in list(material_consumed_by_tasks.values()) for item in sublist]
# merged_list.sort()
# print(merged_list == tasks)

# count = 0
# for k in materials:
#   for n in time_points[1:]:
#     if (net_delivery[(k,n)]):
#       print("net delivery(%s, %.2f): %.2f" % (k, n, net_delivery[(k,n)]))
#       count += 1

# print(count)