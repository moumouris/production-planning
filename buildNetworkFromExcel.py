import pandas as pd
import numpy as np

network_data = pd.read_excel('./case1Network.xlsx', header=None)
print(network_data)
network_array = network_data.to_numpy(na_value=False)


units_and_tasks = network_array[:2]


unit_can_process_tasks = {}

for i in range(1, len(units_and_tasks[0])):
  if units_and_tasks[0][i]:
    current_unit = units_and_tasks[0][i]
    unit_can_process_tasks[current_unit] = [units_and_tasks[1][i]]
  else:
    unit_can_process_tasks[current_unit].append(units_and_tasks[1][i])



material_produced_by_tasks = {}
material_consumed_by_tasks = {}

materials_tasks = network_array[1:]

for i in range(1, len(materials_tasks)):
  material_produced_by_tasks[materials_tasks[i][0]] = []
  material_consumed_by_tasks[materials_tasks[i][0]] = []
  for j in range(len(materials_tasks[0])):
    if materials_tasks[i][j] == 1:
      material_produced_by_tasks[materials_tasks[i][0]].append(materials_tasks[0][j])
    if materials_tasks[i][j] == -1:
      material_consumed_by_tasks[materials_tasks[i][0]].append(materials_tasks[0][j])

