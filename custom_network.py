import networkx as nx
from helpers import *


# Create a directed graph
G = nx.DiGraph()

levels = 4
units_in_level = [3, 5, 4, 6]
material_types = {
   'RM': 4,
   'INA': 6,
   'INB': 5,
   'INC': 7,
   'FP': 14
}

#Generate materials, tasks and units
materials_for_each_type = {}
materials_list = []
for material in material_types:
   materials_for_each_type[material]  = generate_materials(material, material_types[material])
   materials_list.extend(materials_for_each_type[material])
units = generate_units(units_in_level)
tasks, unit_can_process_tasks = generate_tasks(units)

#Add coordinates to task nodes
task_levels_length = compute_task_levels_length(unit_can_process_tasks)
task_position, rectangles = compute_task_positions(unit_can_process_tasks, task_levels_length)

#Add coordinates to material nodes
material_position = {}
total_levels = len(materials_for_each_type) + len(task_levels_length)
y_first = total_levels + 2
max_level_length = max(task_levels_length)
for i, material_type in enumerate(materials_for_each_type):
   y = y_first - (6 * i)
   x = (max_level_length - material_types[material_type]) / 2
   for material in materials_for_each_type[material_type]:
      material_position[material] = x, y
      x += 1

#final coordinates
task_position.update(material_position)
position = task_position

# Add nodes
type_b_nodes = tasks
G.add_nodes_from(type_b_nodes, node_type='B')
type_a_nodes = materials_list
G.add_nodes_from(type_a_nodes, node_type='A')



# # Add edges between nodes
# edges = [
#     ('RM1', 'T11'),
#     ('RM1', 'T21'),
#     ('RM2', 'T12'),
#     ('RM2', 'T22'),
#     ('T11', 'FP1'),
#     ('T12', 'FP2'),
#     ('T21', 'FP2'),
#     ('T22', 'FP1')
#     ]
# G.add_edges_from(edges)

# Define positions for the nodes (optional)

# pos = {
#     'RM1': (-1, 2),
#     'RM2': (1, 2),
#     'T11': (-2, 1),
#     'T12': (-1, 1),
#     'T21': (1, 1),
#     'T22': (2, 1),
#     'FP1': (-1,0),
#     'FP2': (1,0)
# } 

# Create a dictionary to map node types to shapes and colors
node_shapes = {'A': 'o', 'B': 's'}
node_colors = {'A': 'red', 'B': 'blue'}

# Customize the appearance of the graph
plt.figure(figsize=(64, 96))
plt.axis('off')
plt.title("Network Process 3")

# Draw the nodes with different marker styles and colors
for node in G.nodes:
    node_type = G.nodes[node]['node_type']
    shape = node_shapes[node_type]
    color = node_colors[node_type]
    nx.draw_networkx_nodes(G, task_position, nodelist=[node], node_color='lightgray', edgecolors = 'black', node_shape=shape, node_size=600)
    nx.draw_networkx_labels(G, task_position, labels={node: node}, font_color='black', font_size=8)

# Draw the edges
# nx.draw_networkx_edges(G, pos, edgelist=G.edges(), edge_color='gray', arrowsize = 20)
for rectangle in rectangles:
  ax = plt.gca()
  ax.add_patch(rectangle[1])
  # ax.add_patch(rectangle[0])

plt.show()

