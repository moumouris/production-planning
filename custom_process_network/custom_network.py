import networkx as nx
import math
from helpers import *
import gurobipy as gp
from gurobipy import GRB
import pickle

random.seed(42)

# Create a directed graph
G = nx.DiGraph()

#Generate materials, tasks and units
materials_for_each_type = {}
materials_list = []
for material in material_types:
   materials_for_each_type[material]  = generate_materials(material, material_types[material])
   materials_list.extend(materials_for_each_type[material])
units = generate_units(units_in_level)
tasks, unit_can_process_tasks = generate_tasks(units)

#save data
with open('unit_can_process_tasks.pkl', 'wb') as file:
    pickle.dump(unit_can_process_tasks, file)
with open('materials_for_each_type.pkl', 'wb') as file:
    pickle.dump(materials_for_each_type, file)

#Add coordinates to task nodes
task_levels_length = compute_task_levels_length(unit_can_process_tasks)
task_position, rectangles = compute_task_positions(unit_can_process_tasks, task_levels_length)

#Add coordinates to material nodes
material_position = {}
total_levels = len(materials_for_each_type) + len(task_levels_length)
max_level_length = max(task_levels_length)
y_first = total_levels + 2
for i, material_type in enumerate(materials_for_each_type):
   y = y_first - (6 * i)
   if ( i == 0 ):
      start = (max_level_length - task_levels_length[i]) / 2
      node_distance = task_levels_length[i] / material_types[material_type]
   elif (  i == ( len(materials_for_each_type) - 1 ) ):
      start = (max_level_length - task_levels_length[i - 1]) / 2
      node_distance = task_levels_length[i - 1] / material_types[material_type]
   else:
      average_length = ( task_levels_length[i-1] + task_levels_length[i] ) / 2
      start = ( max_level_length - average_length) / 2
      node_distance = average_length / material_types[material_type]
   x = start
   for material in materials_for_each_type[material_type]:
      material_position[material] = x, y
      x += node_distance * 1.1

#final coordinates
task_position.update(material_position)
position = task_position

# Add nodes
G.add_nodes_from(tasks, node_type='task')
G.add_nodes_from(materials_list, node_type='material')

# Add edges between nodes
G.add_edges_from(edges)

# Create a dictionary to map node types to shapes
node_shapes = {'material': 'o', 'task': 's'}

# Don't show the axis
plt.axis('off')

# Draw the nodes with different marker styles
for node in G.nodes:
    node_type = G.nodes[node]['node_type']
    shape = node_shapes[node_type]
    nx.draw_networkx_nodes(G, position, nodelist=[node], node_color='lightgray', edgecolors = 'black', node_shape=shape, node_size=400)
    nx.draw_networkx_labels(G, position, labels={node: node}, font_color='black', font_size=6)

# Draw the edges
nx.draw_networkx_edges(G, position, edgelist=G.edges(), edge_color='black', arrowsize = 20)

for rectangle in rectangles:
  ax = plt.gca()
  ax.add_patch(rectangle[1])

plt.show()

with open("custom_process_network.pkl", "wb") as file:
    pickle.dump(G, file)
   
material_produced_by_tasks = {}
material_consumed_by_tasks = {}
for material in materials_list:
   material_produced_by_tasks[material] = list(G.predecessors(material))
   material_consumed_by_tasks[material] = list(G.successors(material))

Dt = 2
capacities_per_material_type = {
   'RM': 90,
   'INA': 4,
   'INB': 5,
   'INC': 4.5,
   'FP': 12,
}

#Generate capacities
capacities = {}
for material_type in materials_for_each_type:
   for material in materials_for_each_type[material_type]:
      capacities[material] = capacities_per_material_type[material_type]

#Generate production costs
task_possible_production_costs = [1.5, 2, 1, 3]
task_production_costs = {}
for task in tasks:
   task_production_costs[task] = random.choice(task_possible_production_costs)

#Generate daily production rates
task_possible_production_rates = [1.5, 2, 1, 3]
task_daily_production_rates = {}
task_production_rates = {}
for task in tasks:
   task_daily_production_rates[task] = random.choice(task_possible_production_rates)
   task_production_rates[task] = task_daily_production_rates[task] * (Dt /24)

#Generate storage costs
storage_costs = {}
possible_storage_costs_for_final_products = [float(i)/10 for i in range(1, 15) ]
for material_type in materials_for_each_type:
   for material in materials_for_each_type[material_type]:
      if material_type == 'FP':
         storage_costs[material] = random.choice(possible_storage_costs_for_final_products)
      else:
         storage_costs[material] = 0

#Generate onhand inventory
onhand_inventory = {}
for material_type in materials_for_each_type:
   for material in materials_for_each_type[material_type]:
      if material_type == 'RM':
         onhand_inventory[material] = 80
      else:
         onhand_inventory[material] = 0

weeks = 8
days = 56

time_points = [i for i in range(int(days * (24 / Dt)) + 1)]

#Generate net delivery
net_delivery = {}
for k in materials_list:
  for n in time_points[1:]:
    net_delivery[(k,n)] = 0

fp_delivery_interval = 7
rm_delivery_interval = 14
#net_delivery for final products
for i, k in enumerate(materials_list[-12:]):
  for j, n in enumerate(range(int(fp_delivery_interval * (24 / Dt)), time_points[-1] + 1, int(fp_delivery_interval * (24 / Dt)))):
    net_delivery[(k,n)] = - math.ceil(random.uniform(0, 6)) / 2

#net_delivery for raw materials_list
for k in materials_list[:4]:
  for i,n in enumerate(range(int(rm_delivery_interval * (24 / Dt) ), time_points[int(rm_delivery_interval * (24 / Dt) ) * 4 + 1], int(rm_delivery_interval * (24 / Dt) ))):
    net_delivery[(k,n)] = math.ceil(random.uniform(10, 24)) / 2


time_periods = [i for i in range(1, int(weeks * 24 * 7 / Dt) + 1)]

#Here goes the model
m = gp.Model("production-planning-simple")
#Define model variables
w = m.addVars(tasks, time_periods, vtype=GRB.BINARY, name="w")
w_s = m.addVars(units, time_periods, vtype=GRB.BINARY, name="w_s")

s = m.addVars(materials_list, time_points[1:], vtype=GRB.CONTINUOUS, lb=0, name="s")
#Define objective function
obj = sum( storage_costs[k] * Dt / 24 * s[k,n] for k in materials_list for n in time_points[1:]) + \
      sum(task_production_costs[i] * task_production_rates[i] * w[i,n] for n in time_periods for i in tasks)

m.setObjective(obj, GRB.MINIMIZE)
#Define constraints
capacity_constraint = m.addConstrs(s[k,n] <= capacities[k] for k in materials_list for n in time_points[1:])

assignment = m.addConstrs(sum(w[i,n] for i in unit_can_process_tasks[j]) + w_s[j,n] == 1 \
  for j in units for n in time_periods)

initial_balance = m.addConstrs(s[k,1] == onhand_inventory[k] + net_delivery[k,1] \
  + sum(task_production_rates[i] * w[i,1] for i in material_produced_by_tasks[k]) \
  - sum(task_production_rates[i] * w[i,1] for i in material_consumed_by_tasks[k]) \
                             for k in materials_list )
                             
balance = m.addConstrs(s[k,n] == s[k,n-1] + net_delivery[k,n] \
  + sum(task_production_rates[i] * w[i,n] for i in material_produced_by_tasks[k]) \
  - sum(task_production_rates[i] * w[i,n] for i in material_consumed_by_tasks[k]) \
  for k in materials_list for n in time_points[2:] )
            
m.write( 'test.lp' )

m.optimize()

status = m.Status
