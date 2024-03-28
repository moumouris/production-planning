import pandas as pd
import numpy as np
from utils import utils
from classes.model1 import Model1
from classes.model2 import Model2
from classes.model3 import Model3


network_data = pd.read_excel('./networkBuilder/case1/case1Network.xlsx', header=None)
network = utils.get_network_from_dataframe(network_data)

material_parameters = pd.read_excel('./networkBuilder/case1/MaterialParameters.xlsx', header=None, index_col=0)
material_parameters = utils.get_material_parameters_from_dataframe(material_parameters)

task_parameters = pd.read_excel('./networkBuilder/case1/TaskParameters.xlsx', header=None, index_col=0)
task_parameters = utils.get_task_parameters_from_dataframe(task_parameters)

parameters = {}
with open('./networkBuilder/case1/parameters.txt', 'r') as file:
    for line in file:
        key, value = line.strip().split('=')
        parameters[key.strip()] = int(value.strip())

time_points = [i for i in range(int(parameters['planning_horizon'] * 24 / parameters['Dt']) + 1)]
time_periods = [i for i in range(1, int(parameters['planning_horizon'] * 24 / parameters['Dt']) + 1)]

net_delivery_df = pd.read_excel('./networkBuilder/case1/NetDelivery.xlsx', header=None)
net_delivery_array = net_delivery_df.to_numpy(na_value=False)

net_delivery= {}
for i,k in enumerate(network['materials']):
  for n in time_points:
    net_delivery[(k,n)] = 0

    if n % parameters['delivery_interval'] == 0 and n > 0:
      net_delivery[(k,n)] = -net_delivery_array[i + 2][int(n / parameters['delivery_interval'])]
      print(k, n, net_delivery[(k,n)])

parameters['net_delivery'] = net_delivery
parameters['days_duration'] = parameters['planning_horizon']

parameters.update(task_parameters)
parameters.update(material_parameters)

print(parameters)
model1 = Model1(network, parameters)

model1.m.optimize()