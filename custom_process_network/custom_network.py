import networkx as nx
from helpers import *
import pickle
from gurobipy import GRB
import pandas as pd
from utils.utils import calculate_net_delivery
from classes.model1 import Model1
from classes.model2 import Model2
from classes.model3 import Model3

# Create a directed graph
G = nx.DiGraph()

#Generate materials, tasks and units
materials_for_each_type = {}
materials_list = []
for material in num_of_materials_in_each_type:
   materials_for_each_type[material]  = generate_materials(material, num_of_materials_in_each_type[material])
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
      node_distance = task_levels_length[i] / num_of_materials_in_each_type[material_type]
   elif (  i == ( len(materials_for_each_type) - 1 ) ):
      start = (max_level_length - task_levels_length[i - 1]) / 2
      node_distance = task_levels_length[i - 1] / num_of_materials_in_each_type[material_type]
   else:
      average_length = ( task_levels_length[i-1] + task_levels_length[i] ) / 2
      start = ( max_level_length - average_length) / 2
      node_distance = average_length / num_of_materials_in_each_type[material_type]
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
for node, data in G.nodes( data=True ):
    node_type = data.get('node_type')
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

Dts = [2, 4, 6, 12]
weeks = 6
days = 42
delivery_interval = 7
time_limit_for_gurobi = 1200 #seconds
net_delivery_ceiling_model1 = 3
net_delivery_ceiling_model2n3 = 6 

results = {}
for Dt in Dts:
   results[Dt] = {}
   random.seed(42)

   time_periods = [i for i in range(1, int(weeks * 24 * 7 / Dt) + 1)]
   time_points = [i for i in range(int(days * (24 / Dt)) + 1)]

   capacities_per_material_type = {
      'RM': 200,
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

   #Generate production costs
   task_possible_production_costs = [1.5, 2, 1, 3]
   task_production_costs = {}
   for task in tasks:
      task_production_costs[task] = random.choice(task_possible_production_costs)

   #Generate production rates
   task_possible_daily_production_rates = [2, 2, 1.5, 3]
   task_daily_production_rates = {}
   task_production_rates = {}
   for task in tasks:
      task_daily_production_rates[task] = random.choice(task_possible_daily_production_rates)
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
            onhand_inventory[material] = 200
         else:
            onhand_inventory[material] = 0

   net_delivery_model1 = calculate_net_delivery(materials_list, num_of_materials_in_each_type['FP'], int(delivery_interval * (24 / Dt)), time_points, ceiling=net_delivery_ceiling_model1, lamda = 4)
   net_delivery_model2n3 = calculate_net_delivery(materials_list, num_of_materials_in_each_type['FP'], int(delivery_interval * (24 / Dt)), time_points, ceiling=net_delivery_ceiling_model2n3, lamda = 4)
   
   network = {}
   network['tasks']                      = tasks
   network['materials']                  = materials_list
   network['units']                      = units
   network['unit_can_process_tasks']     = unit_can_process_tasks
   network['material_consumed_by_tasks'] = material_consumed_by_tasks
   network['material_produced_by_tasks'] = material_produced_by_tasks

   parameters = {}
   parameters['material_storage_cost']      = storage_costs
   parameters['task_production_cost']       = task_production_costs
   parameters['task_daily_production_rate'] = task_daily_production_rates
   parameters['Dt']                         = Dt 
   parameters['onhand_inventory']           = onhand_inventory
   parameters['capacity']                   = capacities

   parameters_model1 = dict(parameters)
   parameters_model1['days_duration'] = days
   parameters_model1['net_delivery'] = net_delivery_model1

   parameters_model2n3 = dict(parameters)
   parameters_model2n3['net_delivery'] = net_delivery_model2n3
   parameters_model2n3['number_of_raw_materials']          = num_of_materials_in_each_type['RM']
   parameters_model2n3['number_of_intermediate_materials'] = len(materials_list) - num_of_materials_in_each_type['RM'] - num_of_materials_in_each_type['FP']
   parameters_model2n3['days_duration'] = days

   model1 = Model1(network, parameters_model1)
   model2 = Model2(network, parameters_model2n3)
   model3 = Model3(network, parameters_model2n3)

   
   models = [model1, model2, model3]
   for i,model in enumerate(models):
      model.m.setParam('timeLimit', time_limit_for_gurobi)
      print('##################### Dt = ' + str(Dt) + ' #########################')
      model.m.optimize()
      obj = model.m.getObjective()
      obj_value = obj.getValue()
      integrality_gap = model.m.MIPGap

      lp_relaxation_model = model.m.relax()
      lp_relaxation_model.optimize()
      lp_obj = lp_relaxation_model.getObjective()
      lp_obj_value = lp_obj.getValue()
      min_integrality_gap =  ( obj_value * (1 - integrality_gap) - lp_obj_value ) / ( obj_value * (1 - integrality_gap) )
      max_integrality_gap = (obj_value - lp_obj_value) / obj_value
      model_name = 'M' + str((i + 1))
      if model.m.status == GRB.TIME_LIMIT:
         print("Model was interrupted due to reaching the time limit.")
         status = "interrupted"
      else:
         print("Optimization completed successfully.")
         status = "successful"

      results[Dt][model_name] = {
         'objective': obj_value,
         'integrality gap': integrality_gap * 100, 
         'status': status,
         'min integrality gap': min_integrality_gap * 100,
         'max integrality gap': max_integrality_gap * 100,
         'lp objective': lp_obj_value
         }
   

for time_partition in list(results.keys()):
   print ('######################   ' + 'Dt: ' + str(time_partition) + '   ##########################')
   for model_name in list(results[time_partition].keys()):
      print(model_name, results[time_partition][model_name])


#################### EXPORT DATA ##############################
material_parameters = {'material': materials_list, 
                       'capacity': capacities.values(),
                       'storage cost': storage_costs.values(),
                       'onhand inventory': onhand_inventory.values()
                      }
materials_table = pd.DataFrame(material_parameters)
materials_table.to_csv('data/custom-network/materials.csv', index=False)

task_parameters = {'task': tasks,
                   'production cost': task_production_costs.values() 
                  }

tasks_table = pd.DataFrame(task_parameters)
tasks_table.to_csv('data/custom-network/tasks.csv', index=False)

demand = {}
for material in materials_list[len(materials_list) - num_of_materials_in_each_type['FP']:]:
  demand[material] = []
  for n in range(delivery_interval * 2, time_points[-1] + 1, delivery_interval * 2):
      demand[material].append( -(net_delivery_model1[(material, n)]))

demand_table = pd.DataFrame(demand, index=[i for i in range(1, weeks + 1)])
demand_table.index.name = 'week'
demand_table.to_csv('data/custom-network/model1-demand.csv')

demand = {}
for material in materials_list[len(materials_list) - num_of_materials_in_each_type['FP']:]:
  demand[material] = []
  for n in range(2 * delivery_interval, time_points[-1] + 1, 2 * delivery_interval):
      demand[material].append( -(net_delivery_model2n3[(material, n)]))

demand_table = pd.DataFrame(demand, index=[i for i in range(1, weeks + 1)])
demand_table.index.name = 'week'
demand_table.to_csv('data/custom-network/model2n3-demand.csv')



with open('custom_process_network/results.pkl', 'wb') as file:
    pickle.dump(results, file)