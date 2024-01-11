import gurobipy as gp
from gurobipy import GRB
from classes.model1 import Model1

def make_dict_from_lists(keys, values):
  key_value_pairs = zip(keys, values)
  return dict(key_value_pairs)

class Model2(Model1):
  def __init__(self, network, network_parameters, name='production_planning_with_unmet_demand'):
    super()._initializeParameters(network, network_parameters)
    self.m = gp.Model(name)
    self.w, self.w_s, self.s, self.u = self._addModelVars()
    self._addModelConstraints()
    self._setObjective()
  
  def _addModelVars(self):
    materials = self.network['materials']
    w, w_s, s = super()._addModelVars()
    u = self.m.addVars(materials, self.time_points, vtype=GRB.CONTINUOUS, lb=0, name="u")
    return w, w_s, s, u
  
  def _addModelConstraints(self):
    super()._addCapacityConstraint()
    self._addUnmetDemandConstraint()
    super()._addAssignmentConstraint()
    self._addBalanceConstraints()

  def _setObjective(self):
    obj = self._calcObjectiveFunction()
    self.m.setObjective(obj, GRB.MINIMIZE)

  def _addUnmetDemandConstraint(self):
    materials = self.network['materials']
    rm_num    = self.parameters['number_of_raw_materials']
    intm_num  = self.parameters['number_of_intermediate_materials']

    unmet_demand_for_rm_n_int_materials = \
    self.m.addConstrs(self.u[k,n] == 0 for k in materials[:rm_num + intm_num] for n in  self.time_points)
    
  def _addBalanceConstraints(self):
    material_produced_by_tasks = self.network['material_produced_by_tasks']
    material_consumed_by_tasks = self.network['material_consumed_by_tasks']
    onhand_inventory           = self.parameters['onhand_inventory']
    net_delivery               = self.parameters['net_delivery']
    materials                  = self.network['materials']

    initial_balance = self.m.addConstrs(self.s[k,1] - self.u[k,1] == -self.u[k,0] + onhand_inventory[k] + net_delivery[k,1] \
    + sum(self.task_production_rates[i] * self.w[i,1] for i in material_produced_by_tasks[k]) \
    - sum(self.task_production_rates[i] * self.w[i,1] for i in material_consumed_by_tasks[k]) \
                              for k in materials )
                              
    balance = self.m.addConstrs(self.s[k,n] -self.u[k,n]== self.s[k,n-1] -self.u[k,n-1]+ net_delivery[k,n] \
    + sum(self.task_production_rates[i] * self.w[i,n] for i in material_produced_by_tasks[k]) \
    - sum(self.task_production_rates[i] * self.w[i,n] for i in material_consumed_by_tasks[k]) \
    for k in materials for n in self.time_points[2:] )

  def _calcObjectiveFunction(self):
    materials             = self.network['materials']
    material_storage_cost = self.parameters['material_storage_cost']
    Dt                    = self.parameters['Dt']

    obj_without_unmet_demand_costs = super()._calcObjectiveFunction()
    obj = obj_without_unmet_demand_costs +  \
      sum( 50 * material_storage_cost[k] * Dt / 24 * self.u[k,n] for k in materials for n in self.time_points)
    return obj
  