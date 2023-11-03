import random
import matplotlib.pyplot as plt

random.seed(42)
possible_numbers_of_tasks_in_unit = [2,3,4,5]

def generate_units(units_in_level):
  units = []
  for index, num_of_units in enumerate(units_in_level):
      for i in range(num_of_units):
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

def compute_task_levels_length(unit_can_process_tasks):
  task_levels_length = []
  first_level = '1'
  level = first_level
  level_length = 0
  for i,unit in enumerate(unit_can_process_tasks):
    if unit[1] != level:
      level = unit[1]
      task_levels_length.append(level_length)
      level_length = 0
    else:
      if(i != 0):
        level_length += 1
  
    level_length += len(unit_can_process_tasks[unit])

  task_levels_length.append(level_length)

  return task_levels_length

def compute_task_positions(unit_can_process_tasks, task_levels_length):
  max_level_length = max(task_levels_length)
  pos = {}
  first_level = 1
  level = first_level
  x,y = ((max_level_length - task_levels_length[level - 1]) / 2), len(task_levels_length) * 2
  unit_rectangles = []
  for i,unit in enumerate(unit_can_process_tasks):
    if int(unit[1]) != level:
      level = int(unit[1])
      y = y - 6
      x = ( max_level_length - task_levels_length[level - 1] ) / 2
    else:
      if i != 0:
        x += 1
    unit_rectangles.append(draw_unit_rectangle(x, y, len(unit_can_process_tasks[unit]), unit))
    for task in unit_can_process_tasks[unit]:
      pos[task] = (x, y)
      x += 1
  
  return pos, unit_rectangles


def draw_unit_rectangle(x_start, y_start, width, unit):
    width = width + 0.2
    height = 1.2
    x,y = x_start - 0.6, y_start - 0.9
    rectangle = plt.Rectangle((x,y), width, height, edgecolor='black', facecolor='none', linestyle='--')
    label  = plt.text(x + width / 2, y + height + 1.2, unit, ha='center', va='top', color='red')
    return label,rectangle

def generate_materials(material_type, number_of_materials):
   materials = [(material_type + str(i + 1)) for i in range(number_of_materials)]
   return materials
    