# -*- coding: utf-8 -*-
"""
Created on Sat Apr  3 14:55:46 2021

@author: Vincent Reurslag
"""
import pandas as pd
from pyomo.environ import *

def flatten_dict(d):
    def items():
        for key, value in d.items():
            if isinstance(value, dict):
                for subkey, subvalue in flatten_dict(value).items():
                    if type(key) == int:
                        yield (key,) + (subkey,), subvalue
                    else:
                        yield key + (subkey,), subvalue
            else:
                yield key, value

    return dict(items())

class Superstructure:
    def __init__(self, xlsx_file):
        """Initializes the superstructure by getting the indices j,k,i,u and corresponding names
        NOTE: Leave the excel tabs empty besides the corresponding tables"""

        df = pd.read_excel(xlsx_file,'Superstructure j,k')
        j = list(df.iloc[0,2:])
        k = list(df.iloc[1:,1])
        equipment_names = df.iloc[1:, 2:]
        
        
        equipment_names.index = k
        equipment_names.columns = j
        equipment_names.index.name = 'k'
        equipment_names.columns.name = 'j'
        
        df = pd.read_excel(xlsx_file,'Components i')
        i = list(df.iloc[1:,0])
        component_names = df.iloc[1:,1]
        component_names.index = i
        component_names.index.name = 'i'
        
        df = pd.read_excel(xlsx_file,'Utilities u')
        u = list(df.iloc[1:,0])
        utilities_names = df.iloc[1:,1]
        utilities_names.index = u
        utilities_names.index.name = 'u'
    
        self.j = j
        self.k = k
        self.i = i
        self.u = u
        self.equipment_names = equipment_names
        self.component_names = component_names
        self.utilities_names = utilities_names
        
    def get_SF(self,xlsx_file):
        df = pd.read_excel(xlsx_file, 'SF j,k,i')
        SF_data = df.iloc[2:,2:]
        columns = pd.MultiIndex.from_product([self.j,self.k])
        SF_data.columns = columns
        SF_data.index = self.i
        SF_data.columns.names = ['j','k']
        SF_data.index.name = 'i'
        SF_data = SF_data.to_dict()
        SF_data = flatten_dict(SF_data)
        self.SF_data = SF_data
        
    def get_EC(self,xlsx_file):
        df = pd.read_excel(xlsx_file, 'EC j,k')
        EC_data = df.iloc[1:,2:]
        EC_data.columns = self.j
        EC_data.index = self.k
        EC_data.columns.name = 'j'
        EC_data.index.name = 'k'
        EC_data = EC_data.to_dict()
        EC_data = flatten_dict(EC_data)
        self.EC_data = EC_data
        
    def get_F0(self,xlsx_file):
        df = pd.read_excel(xlsx_file, 'Flow0 i')
        F0_data = df.iloc[1:,2]
        F0_data.index = self.i
        F0_data.index.name = 'i'
        F0_data = F0_data.to_dict()
        self.F0_data = F0_data
        
    def get_results(self,model):
        """Get results from the pyomo model (Logic and flow data)"""
        Flow_data = {(j, k, i): value(flow) for (j, k, i), flow in model.flow.items()}
        Flow_data = pd.DataFrame.from_dict(Flow_data, orient="index", columns=["variable value"])
        Flow_data = Flow_data.values.reshape(len(self.j)*len(self.k),len(self.i)).transpose()
        Flow_data = pd.DataFrame(Flow_data)
        Flow_data.index = self.i
        Flow_data.index.name = 'i'
        columns = pd.MultiIndex.from_product([self.j,self.k])
        Flow_data.columns = columns
        Flow_data.columns.names = ['j','k']
        
        
        Logic_data = {(j,k) : value(y) for (j, k), y in model.y.items()}
        Logic_data = pd.DataFrame.from_dict(Logic_data, orient="index", columns=["variable value"])
        Logic_data = Logic_data.values.reshape(len(self.j),len(self.k)).transpose()
        Logic_data = pd.DataFrame(Logic_data)
        Logic_data.index = self.k
        Logic_data.index.name = 'k'
        Logic_data.columns = self.j
        Logic_data.columns.name = 'j'
        
        self.Flow_data = Flow_data
        self.Logic_data = Logic_data
    
        
        
        


