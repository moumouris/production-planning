import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import random

random.seed(42)
possible_numbers_of_tasks_in_unit = [2,3,4,5]

def draw_unit_rectangle(x_start, x_end, y_start, unit):
    width = x_end - x_start + 0.6
    height = 0.4
    x,y = x_start - 0.3, y_start - 0.2
    print(width, height, x, y)
    rectangle = plt.Rectangle((x,y), width, height, edgecolor='black', facecolor='none', linestyle='--')
    plt.text(x + width / 2, y + height + 0.1, unit, ha='center', va='top', color='red')
    return rectangle

# Create a directed graph
G = nx.DiGraph()

levels = 4
units_in_level = [3, 5, 4, 6]

def generate_units(units_in_level):
  units = []
  for index, item in enumerate(units_in_level):
      for i in range(item):
        unit = 'U' + str(index + 1) + str(i + 1)
        units.append(unit)
  
  return units

def generate_tasks(units):
  tasks = []
  unit_can_process_tasks = {}
  for unit in units:
    task_number = random.choice(possible_numbers_of_tasks_in_unit)
    for i in range(task_number):
      task = 'T' + unit[1:3] + str(i + 1)
      tasks.append(task)
      
    unit_can_process_tasks[unit] = tasks[-task_number:]
    
  
  return tasks, unit_can_process_tasks

units = generate_units(units_in_level)
tasks, unit_can_process_tasks = generate_tasks(units)

# Add nodes of Type A
type_a_nodes = tasks
G.add_nodes_from(type_a_nodes, node_type='A')

# # Add nodes of Type B
# type_b_nodes = ['T11', 'T12', 'T21', 'T22']
# G.add_nodes_from(type_b_nodes, node_type='B')

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

pos = {
    'RM1': (-1, 2),
    'RM2': (1, 2),
    'T11': (-2, 1),
    'T12': (-1, 1),
    'T21': (1, 1),
    'T22': (2, 1),
    'FP1': (-1,0),
    'FP2': (1,0)
} 

# Create a dictionary to map node types to shapes and colors
node_shapes = {'A': 'o', 'B': 's'}
node_colors = {'A': 'red', 'B': 'blue'}

# Customize the appearance of the graph
plt.figure(figsize=(8, 6))
plt.axis('off')
plt.title("Directed Network Graph with Grouped Nodes")

material_fp1_produced_by_tasks = list(G.successors('RM1'))
# Draw the nodes with different marker styles and colors
for node in G.nodes:
    node_type = G.nodes[node]['node_type']
    shape = node_shapes[node_type]
    color = node_colors[node_type]
    nx.draw_networkx_nodes(G, pos, nodelist=[node], node_color=color, node_shape=shape, node_size=800)
    nx.draw_networkx_labels(G, pos, labels={node: node}, font_color='black', font_size=10)

# Draw the edges
nx.draw_networkx_edges(G, pos, edgelist=G.edges(), edge_color='gray', arrowsize = 20)

# rectangle = draw_unit_rectangle(-2, -1, 1)
# plt.gca().add_patch(rectangle)

plt.show()

