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
   'FP': 12
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
type_b_nodes = tasks
G.add_nodes_from(type_b_nodes, node_type='B')
type_a_nodes = materials_list
G.add_nodes_from(type_a_nodes, node_type='A')



# Add edges between nodes
edges = [
    ('RM1', 'T111'),
    ('RM1', 'T112'),
    ('RM2', 'T121'),
    ('RM2', 'T122'),
    ('RM3', 'T131'),
    ('RM3', 'T132'),
    ('RM4', 'T133'),
    ('RM4', 'T134'),
    ('T111', 'INA2'),
    ('T112', 'INA1'),
    ('T121', 'INA4'),
    ('T122', 'INA3'),
    ('T131', 'INA3'),
    ('T132', 'INA4'),
    ('T133', 'INA5'),
    ('T134', 'INA6'),
    ('INA1', 'T211'),
    ('INA1', 'T221'),
    ('INA1', 'T231'),
    ('INA2', 'T212'),
    ('INA2', 'T222'),
    ('INA2', 'T232'),
    ('INA3', 'T213'),
    ('INA3', 'T223'),
    ('INA4', 'T241'),
    ('INA5', 'T233'),
    ('INA5', 'T251'),
    ('INA6', 'T252'),
    ('INA6', 'T242'),
    ('T211', 'INB1'),
    ('T212', 'INB1'),
    ('T213', 'INB1'),
    ('T221', 'INB2'),
    ('T222', 'INB2'),
    ('T223', 'INB2'),
    ('T231', 'INB3'),
    ('T232', 'INB3'),
    ('T233', 'INB3'),
    ('T241', 'INB4'),
    ('T242', 'INB4'),
    ('T251', 'INB5'),
    ('T252', 'INB5'),
    ('INB1', 'T311'),
    ('INB1', 'T312'),
    ('INB2', 'T313'),
    ('INB2', 'T314'),
    ('INB2', 'T315'),
    ('INB3', 'T321'),
    ('INB3', 'T331'),
    ('INB4', 'T322'),
    ('INB4', 'T332'),
    ('INB5', 'T341'),
    ('INB5', 'T342'),
    ('T311', 'INC1'),
    ('T312', 'INC2'),
    ('T313', 'INC2'),
    ('T314', 'INC3'),
    ('T315', 'INC4'),
    ('T321', 'INC4'),
    ('T322', 'INC5'),
    ('T331', 'INC5'),
    ('T332', 'INC6'),
    ('T341', 'INC6'),
    ('T342', 'INC7'),
    ('INC1', 'T411'),
    ('INC1', 'T412'),
    ('INC2', 'T413'),
    ('INC2', 'T421'),
    ('INC2', 'T422'),
    ('INC3', 'T423'),
    ('INC3', 'T431'),
    ('INC3', 'T432'),
    ('INC4', 'T441'),
    ('INC4', 'T442'),
    ('INC4', 'T443'),
    ('INC5', 'T451'),
    ('INC5', 'T452'),
    ('INC5', 'T453'),
    ('INC6', 'T454'),
    ('INC6', 'T455'),
    ('INC7', 'T461'),
    ('INC7', 'T462'),
    ('INC7', 'T463'),
    ('T411', 'FP1'),
    ('T412', 'FP2'),
    ('T413', 'FP3'),
    ('T421', 'FP2'),
    ('T422', 'FP3'),
    ('T423', 'FP4'),
    ('T431', 'FP5'),
    ('T432', 'FP6'),
    ('T441', 'FP5'),
    ('T442', 'FP7'),
    ('T443', 'FP6'),
    ('T451', 'FP8'),
    ('T452', 'FP10'),
    ('T453', 'FP12'),
    ('T454', 'FP9'),
    ('T455', 'FP11'),
    ('T461', 'FP10'),
    ('T462', 'FP11'),
    ('T463', 'FP12'),
    ]
G.add_edges_from(edges)

# Define positions for the nodes (optional)


# Create a dictionary to map node types to shapes and colors
node_shapes = {'A': 'o', 'B': 's'}
node_colors = {'A': 'red', 'B': 'blue'}

# Customize the appearance of the graph
plt.axis('off')

# Draw the nodes with different marker styles and colors
for node in G.nodes:
    node_type = G.nodes[node]['node_type']
    shape = node_shapes[node_type]
    color = node_colors[node_type]
    nx.draw_networkx_nodes(G, position, nodelist=[node], node_color='lightgray', edgecolors = 'black', node_shape=shape, node_size=400)
    nx.draw_networkx_labels(G, position, labels={node: node}, font_color='black', font_size=6)

# Draw the edges
nx.draw_networkx_edges(G, position, edgelist=G.edges(), edge_color='black', arrowsize = 20)
for rectangle in rectangles:
  ax = plt.gca()
  ax.add_patch(rectangle[1])

plt.show()

