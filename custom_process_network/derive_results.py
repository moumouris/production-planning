import pickle as pkl
import pandas as pd

with open('custom_process_network/results.pkl', 'rb') as f:
    results = pkl.load(f)

models = ['M1', 'M2', 'M3']

model_results = {}
for model in models:
  model_results[model] = {key: [] for key in results[2][model].keys()}
  model_results[model]['Dt'] = []
  for Dt in results.keys():  
    model_results[model]['Dt'].append(Dt)
    for key, value in results[Dt][model].items():
      if isinstance(value, str):
         model_results[model][key].append(value)
      else:
        model_results[model][key].append("{:.3f}".format(value))

  model_table = pd.DataFrame(model_results[model])
  model_table.to_csv('data/custom-network/' + model + '.csv', index=False)
print(model_table)