import gurobipy as gp
from gurobipy import GRB
# from utils.utils import make_dict_from_lists

def make_dict_from_lists(keys, values):
  key_value_pairs = zip(keys, values)
  return dict(key_value_pairs)

class Model1:
  def __init__(self, network, network_parameters, name='production_planning_simple'):
    self._initializeParameters(network, network_parameters)
    self.m = gp.Model(name)
    self.w, self.w_s, self.s = self._addModelVars()
    self._addModelConstraints()
    self._setObjective()
  
  def _initializeParameters(self, network, network_parameters):
    self.network               = network
    self.parameters            = network_parameters
    Dt                         = self.parameters['Dt']
    days_duration              = self.parameters['days_duration']
    self.time_points           = [i for i in range(int(days_duration * 24 / Dt) + 1)]
    self.time_periods          = [i for i in range(1, int(days_duration * 24 / Dt) + 1)]
    task_production_rates_list = [ i * (self.parameters['Dt'] / 24 ) 
                                  for i in list(self.parameters['task_daily_production_rate'].values()) ]
    self.task_production_rates = make_dict_from_lists(self.network['tasks'], task_production_rates_list)

  def _addModelVars(self):
    tasks = self.network['tasks']
    units = self.network['units']
    materials = self.network['materials']

    w = self.m.addVars(tasks, self.time_periods, vtype=GRB.BINARY, name="w")
    w_s = self.m.addVars(units, self.time_periods, vtype=GRB.BINARY, name="w_s")
    s = self.m.addVars(materials, self.time_points[1:], vtype=GRB.CONTINUOUS, lb=0, name="s")
    return w, w_s, s
  
  def _addModelConstraints(self):
    self._addCapacityConstraint()
    self._addAssignmentConstraint()
    self._addBalanceConstraints()      
    
  def _setObjective(self):
   
    obj = self._calcObjectiveFunction()
    self.m.setObjective(obj, GRB.MINIMIZE)

  def _addCapacityConstraint(self):
    capacities = self.parameters['capacity']
    materials  = self.network['materials']
    capacity_constraint = self.m.addConstrs(self.s[k,n] <= capacities[k] for k in materials for n in self.time_points[1:])

  def _addAssignmentConstraint(self):
    unit_can_process_tasks = self.network['unit_can_process_tasks']
    units                  = self.network['units']
    assignment = self.m.addConstrs(sum(self.w[i,n] for i in unit_can_process_tasks[j]) + self.w_s[j,n] == 1 \
      for j in units for n in self.time_periods)
    
  def _addBalanceConstraints(self):
    materials  = self.network['materials']
    material_produced_by_tasks = self.network['material_produced_by_tasks']
    material_consumed_by_tasks = self.network['material_consumed_by_tasks']
    onhand_inventory           = self.parameters['onhand_inventory']
    net_delivery               = self.parameters['net_delivery']

    initial_balance = self.m.addConstrs(self.s[k,1] == onhand_inventory[k] + net_delivery[k,1] \
      + sum(self.task_production_rates[i] * self.w[i,1] for i in material_produced_by_tasks[k]) \
      - sum(self.task_production_rates[i] * self.w[i,1] for i in material_consumed_by_tasks[k]) \
                                for k in materials )
                                
    balance = self.m.addConstrs(self.s[k,n] == self.s[k,n-1] + net_delivery[k,n] \
      + sum(self.task_production_rates[i] * self.w[i,n] for i in material_produced_by_tasks[k]) \
      - sum(self.task_production_rates[i] * self.w[i,n] for i in material_consumed_by_tasks[k]) \
      for k in materials for n in self.time_points[2:] )
  
  def _calcObjectiveFunction(self):
    tasks                 = self.network['tasks']
    materials             = self.network['materials']
    material_storage_cost = self.parameters['material_storage_cost']
    task_production_cost  = self.parameters['task_production_cost']
    Dt                    = self.parameters['Dt']
    obj = sum( material_storage_cost[k] * Dt / 24 * self.s[k,n] for k in materials for n in self.time_points[1:]) + \
      sum(task_production_cost[i] * self.task_production_rates[i] * self.w[i,n] for n in self.time_periods for i in tasks)
    
    return obj
  