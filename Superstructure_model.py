# -*- coding: utf-8 -*-
"""
Created on Sun Mar 28 16:32:52 2021

@author: Vincent Reurslag
"""

from pyomo.environ import *



def Superstructure_model(Superstructure):
    model = ConcreteModel()
    
    model.j = Set(initialize = Superstructure.j, doc = 'process stages')
    model.k = Set(initialize = Superstructure.k, doc = 'Technology options')
    model.i = Set(initialize = Superstructure.i, doc = 'Species in reaction mixture')
    
    
    model.SF = Param(model.j, model.k, model.i, initialize = Superstructure.SF_data, doc = 'Split factor data for equipment types')
    model.EC = Param(model.j, model.k, initialize = Superstructure.EC_data, doc = 'Cost data for equipment types')
    model.flow0 = Param(model.i, initialize = Superstructure.F0_data, doc = 'Flow coming out of membrane reactor')
    model.M = Param(initialize = 1e5)
    
    model.flow = Var(model.j, model.k, model.i, bounds = (0.0,None), doc = 'Flow at every equipment for every component')
    model.y = Var(model.j, model.k, domain = Binary, doc = 'Logic variable')
    model.TEC = Var(bounds = (0.0, None), doc = 'Total equipment cost')
    model.BDP = Var(bounds = (0.0, None), doc = 'Biodiesel production')
    model.flowtot = Var(model.j, model.k, bounds = (0.0, None))
    model.flowstage = Var(model.j, model.i, bounds = (0.0, None))
    
    def massbalance_rule1(model, j, k, i):
        if j >= 2:
            return model.flow[j,k,i] <= model.flowstage[j-1,i] * model.SF[j,k,i] + model.M * (1-model.y[j,k])
        else:
            return model.flow[j,k,i] == model.flow0[i] * model.SF[j,k,i] * model.y[j,k]
        
    def massbalance_rule2(model, j, k, i):
        if j >= 2:
            return model.flow[j,k,i] >= model.flowstage[j-1,i] * model.SF[j,k,i] - model.M * (1-model.y[j,k])
        else:
            return Constraint.Skip
    
    def massbalance_rule3(model, j, k, i):
        if j >= 2:
            return model.flow[j,k,i] <= model.M * model.y[j,k]
        else:
            return Constraint.Skip
    
    model.massrule1 = Constraint(model.j, model.k, model.i, rule = massbalance_rule1)
    model.massrule2= Constraint(model.j, model.k, model.i, rule = massbalance_rule2)
    model.massrule3 = Constraint(model.j, model.k, model.i, rule = massbalance_rule3)
    
    def flowstage_rule(model, j, i):
        return model.flowstage[j,i] == sum(model.flow[j,k,i] for k in model.k)
    
    model.flowstage_rule = Constraint(model.j, model.i, rule = flowstage_rule)
    
    def logic_rule(model, j):
        return sum(model.y[j,k] for k in model.k) == 1
    
    model.logic = Constraint(model.j, rule = logic_rule, doc = 'One option per stage')
    
    def BDP_rule(model):
        return model.BDP == model.flow[5,1,1]
    
    model.BDP_rule = Constraint(rule = BDP_rule, doc = 'Biodiesel produced')
    
    def flowtot_rule(model, j, k):
        return model.flowtot[j,k] == sum(model.flow[j,k,i] for i in model.i) 
    
    model.flowtot_rule = Constraint(model.j, model.k, rule = flowtot_rule)
    
    def TEC_rule(model):
        return model.TEC == sum(model.EC[j,k] * model.flowtot[j,k] for j in model.j for k in model.k)
    
    model.TEC_rule = Constraint(rule = TEC_rule)
    
    def objective_rule(model):
        return model.TEC
    
    model.objective = Objective(rule = objective_rule, sense = minimize)
    
    
    def pyomo_postprocess(options=None, instance=None, results=None):
      model.flow.display()
      model.y.display()
      model.flowtot.display()
    
    
    # This emulates what the pyomo command-line tools does
    from pyomo.opt import SolverFactory
    import pyomo.environ
    opt = SolverFactory("glpk")
    results = opt.solve(model)
    #sends results to stdout
    results.write()
    print("\nDisplaying Solution\n" + '-'*60)
    #pyomo_postprocess(None, model, results)
    
    return model






