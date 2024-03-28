import matplotlib.pyplot as plt
import numpy as np

np.random.seed(42)
def make_dict_from_lists(keys, values):
  if len(keys) != len(values):
    raise Exception('keys and values should have the same length')
  key_value_pairs = zip(keys, values)
  return dict(key_value_pairs)

def calculate_net_delivery(materials, number_of_final_products, delivery_interval, time_points, ceiling=3, lamda=1):
  np.random.seed(42)
  net_delivery = {}
  for k in materials:
    for n in time_points:
      net_delivery[(k,n)] = 0

  for k in materials[-number_of_final_products:]:
    for n in range(delivery_interval, time_points[-1] + 1, delivery_interval):
      net_delivery[(k,n)] = - np.ceil(ceiling * lamda * np.random.random()) / lamda
  
  return net_delivery

def get_network_from_dataframe(network_data):
  network = {}
  network_array = network_data.to_numpy(na_value=False)
  network['materials'] = network_array.transpose()[0][2:]
  network['tasks'] =  network_array[1][1:]

  units_and_tasks = network_array[:2]

  network['unit_can_process_tasks'] = {}
  for i in range(1, len(units_and_tasks[0])):
    if units_and_tasks[0][i]:
      current_unit = units_and_tasks[0][i]
      network['unit_can_process_tasks'][current_unit] = [units_and_tasks[1][i]]
    else:
      network['unit_can_process_tasks'][current_unit].append(units_and_tasks[1][i])



  network['material_produced_by_tasks'] = {}
  network['material_consumed_by_tasks'] = {}

  materials_tasks = network_array[1:]

  for i in range(1, len(materials_tasks)):
    network['material_produced_by_tasks'][materials_tasks[i][0]] = []
    network['material_consumed_by_tasks'][materials_tasks[i][0]] = []
    for j in range(len(materials_tasks[0])):
      if materials_tasks[i][j] == 1:
        network['material_produced_by_tasks'][materials_tasks[i][0]].append(materials_tasks[0][j])
      if materials_tasks[i][j] == -1:
        network['material_consumed_by_tasks'][materials_tasks[i][0]].append(materials_tasks[0][j])
  
  network['units'] = list(network['unit_can_process_tasks'].keys())

  return network

def get_material_parameters_from_dataframe(material_parameters):
  material_parameters = material_parameters.to_numpy(na_value=False)
  parameters = {}
  parameters['material_storage_cost'] = make_dict_from_lists(material_parameters[1], material_parameters[2])
  parameters['onhand_inventory'] = make_dict_from_lists(material_parameters[1], material_parameters[3])
  parameters['capacity'] = make_dict_from_lists(material_parameters[1], material_parameters[4])

  return parameters

def get_task_parameters_from_dataframe(task_parameters):
  task_parameters = task_parameters.to_numpy(na_value=False)
  parameters = {}
  parameters['task_production_cost'] = make_dict_from_lists(task_parameters[1], task_parameters[2])
  parameters['task_daily_production_rate'] = make_dict_from_lists(task_parameters[1], task_parameters[3])
  return parameters 