import pandas as pd
import numpy as np
import os
import shutil


file_name = input('Enter name of your excel file e.g(example.xlsx): ')
network_data = pd.read_excel('./networkBuilder/' + file_name, header=None)
network_array = network_data.to_numpy(na_value=False)

directory_name = input('Choose a name for your network files directory: ')
os.mkdir('./networkBuilder/' + directory_name)

path =  './networkBuilder/' + directory_name
tasks =  network_array[1][1:]
task_parameters = {
  'tasks': tasks,
  'production cost': np.zeros(len(tasks)),
  'daily production rate': np.zeros(len(tasks)),
}
task_parameters = pd.DataFrame.from_dict(task_parameters, orient='index')
task_parameters.to_excel(path + '/TaskParameters.xlsx')

materials = network_array.transpose()[0][2:]
material_parameters = {
  'materials': materials,
  'storage cost': np.zeros(len(materials)),
  'onhand inventory': np.zeros(len(materials)),
  'capacity': np.zeros(len(materials))
}

material_parameters = pd.DataFrame.from_dict(material_parameters, orient='index')
material_parameters.to_excel(path + '/MaterialParameters.xlsx')

delivery_interval = int(input('Enter delivery interval for materials in days: '))
planning_horizon = int(input('Enter planning horizon in days: '))
number_of_raw_materials = int(input('Enter number of raw materials: '))
number_of_intermediate_materials = int(input('Enter number of intermediate materials: '))
Dt = int(input('Enter Dt partition: '))

parameters_destination = path + 'parameters.tx'
with open(path + '/parameters.txt', 'w') as f:
    f.write('delivery_interval = ' + str(delivery_interval) + '\n')
    f.write('planning_horizon = ' + str(planning_horizon) + '\n')
    f.write('number_of_raw_materials = ' + str(number_of_raw_materials) + '\n')
    f.write('number_of_intermediate_materials = ' + str(number_of_intermediate_materials) + '\n')
    f.write('Dt = ' + str(Dt) + '\n')

net_delivery_table = {}
default_values = []
default_values.append('')
default_values.extend(np.zeros(len(materials)))
for i in range(delivery_interval, planning_horizon + delivery_interval, delivery_interval):
  net_delivery_table[i] = default_values


header = []
header.append('net delivery')
header.extend(materials)
net_delivery_table = pd.DataFrame(net_delivery_table, index=header)
net_delivery_table.to_excel(path + '/NetDelivery.xlsx')

destination = path + '/' + file_name
shutil.copyfile('./networkBuilder/' + file_name, destination)
