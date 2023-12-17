import gurobipy as gp
from gurobipy import GRB
from classes.model2 import Model2

def make_dict_from_lists(keys, values):
  key_value_pairs = zip(keys, values)
  return dict(key_value_pairs)

class Model3(Model2):
  def __init__(self, network, network_parameters, name='production_planning_with_shipments'):
    super()._initializeParameters(network, network_parameters)
    self.m = gp.Model(name)
    self.w, self.w_s, self.s, self.u, self.v = self._addModelVars()
    self._addModelConstraints()
    super()._setObjective()
  
  def _addModelVars(self):
    materials = self.network['materials']
    w, w_s, s, u = super()._addModelVars()
    v = self.m.addVars(materials, self.time_points, vtype=GRB.CONTINUOUS, lb=0, name="v")
    return w, w_s, s, u, v
  
  def _addModelConstraints(self):
    super()._addCapacityConstraint()
    super()._addAssignmentConstraint()
    self._addBalanceConstraints()
    super()._addUnmetDemandConstraint()
    self._addShipmentConstraints()

  def _addBalanceConstraints(self):
    material_produced_by_tasks = self.network['material_produced_by_tasks']
    material_consumed_by_tasks = self.network['material_consumed_by_tasks']
    onhand_inventory           = self.parameters['onhand_inventory']
    net_delivery               = self.parameters['net_delivery']
    materials                  = self.network['materials']
    materials                  = self.network['materials']
    rm_num    = self.parameters['number_of_raw_materials']
    intm_num    = self.parameters['number_of_intermediate_materials']
   #balance and initial balance for raw and intermediate materials 
    initial_balance = self.m.addConstrs(self.s[k,1] == onhand_inventory[k] + net_delivery[k,1] \
      + sum(self.task_production_rates[i] * self.w[i,1] for i in material_produced_by_tasks[k]) \
      - sum(self.task_production_rates[i] * self.w[i,1] for i in material_consumed_by_tasks[k]) \
                                for k in materials[:rm_num + intm_num] )

    balance = self.m.addConstrs(self.s[k,n] == self.s[k,n-1] + net_delivery[k,n] \
      + sum(self.task_production_rates[i] * self.w[i,n] for i in material_produced_by_tasks[k]) \
      - sum(self.task_production_rates[i] * self.w[i,n] for i in material_consumed_by_tasks[k]) \
      for k in materials[:rm_num + intm_num] for n in self.time_points[2:] )

    #balance and initial balance for final products
    initial_balance = self.m.addConstrs(self.s[k,1] + self.v[k,1] == onhand_inventory[k] \
      + sum(self.task_production_rates[i] * self.w[i,1] for i in material_produced_by_tasks[k]) \
      - sum(self.task_production_rates[i] * self.w[i,1] for i in material_consumed_by_tasks[k]) \
      for k in materials[rm_num + intm_num:] )

    balance = self.m.addConstrs(self.s[k,n] + self.v[k,n] == self.s[k, n-1] \
      + sum(self.task_production_rates[i] * self.w[i,n] for i in material_produced_by_tasks[k]) \
      - sum(self.task_production_rates[i] * self.w[i,n] for i in material_consumed_by_tasks[k]) \
      for k in materials[rm_num + intm_num:] for n in self.time_points[2:] )

  
  def _addShipmentConstraints(self):
    net_delivery               = self.parameters['net_delivery']
    materials                  = self.network['materials']
    rm_num    = self.parameters['number_of_raw_materials']
    intm_num    = self.parameters['number_of_intermediate_materials']
    shipments_for_rm_n_int_materials = \
    self.m.addConstrs(self.v[k,n] == 0 for k in materials[:rm_num + intm_num] for n in  self.time_points) 
    shipments_for_fp_materials =  \
    self.m.addConstrs(self.v[k,n] == 0 for k in materials[rm_num + intm_num:] for n in  self.time_points\
      if((n % 7 or n == 0) and n != self.time_points[-1])) 
    shipments = self.m.addConstrs(self.v[k,n] == - self.u[k,n] + self.u[k,n-1] - net_delivery[k,n] for k in materials[rm_num + intm_num:] for n in self.time_points[1:])