import matplotlib.pyplot as plt
import numpy as np

np.random.seed(42)
def make_dict_from_lists(keys, values):
  if len(keys) != len(values):
    raise Exception('keys and values should have the same length')
  key_value_pairs = zip(keys, values)
  return dict(key_value_pairs)

def calculate_net_delivery(materials, number_of_final_products, delivery_interval, time_points, ceiling=3):
  np.random.seed(42)
  net_delivery = {}
  for k in materials:
    for n in time_points:
      net_delivery[(k,n)] = 0

  for k in materials[-number_of_final_products:]:
    for n in range(delivery_interval, time_points[-1] + 1, delivery_interval):
      net_delivery[(k,n)] = - np.ceil(ceiling * np.random.random())
  
  return net_delivery