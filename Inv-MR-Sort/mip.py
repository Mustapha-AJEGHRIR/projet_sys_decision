"""
Mixed integer linear program destined to select a particular feasible set of parameters
see parag 3 in: 
https://www.researchgate.net/publication/221367488_Learning_the_Parameters_of_a_Multiple_Criteria_Sorting_Method
"""

import numpy as np
import pandas as pd
import os
import collections
from gurobipy import Model, GRB, quicksum
from config import solution_saving_path, data_saving_path
from utils import Capturing # to make Gurobi quiet
from instance_generation import mr_sort

class MIPSolver:
    def __init__(
        self,
        data_file=data_saving_path,
        sol_file=solution_saving_path,
        epsilon=0.0000000001,
        M=100,
        verbose=False,
    ):
        self.sol_file = sol_file
        if type(data_file) == str:
            self.data = pd.read_csv(data_file, index_col=0)
        else : # if data_file is a dataframe
            self.data = data_file 
        self.model = None
        self.trained = False
        self.epsilon = epsilon
        self.M = M
        self.p = None
        self.n = None
        self.verbose = verbose
        self.build_model()

    def build_model(self):
        with Capturing() as output:
            m = Model("Mixed integer linear program")
            m.setParam("SolutionLimit", 2) #TODO revoir le sens de la Solutionlimit
            m.setParam("OptimalityTol", 1e-2)

        self.n = n = len(self.data.columns) - 1
        self.p = p = self.data["class"].max()
        
        N = I = range(n)
        K = range(1,p+2)
        K_no_end = K[:-1]

        
        J_h = collections.defaultdict(list, {h : self.data.index[self.data["class"] == h-1] for h in K})
        J = range(len(self.data))
        
        EPSILON = self.epsilon
        M = self.M
        g = lambda i, j: self.data.iloc[j][
            "mark_" + str(i + 1)
        ]  # get mark of instance j in criteria i

        # --------------------------------- Variables -------------------------------- #
        # https://support.gurobi.com/hc/en-us/community/posts/360077803892-Is-there-a-rule-to-write-addvar-or-addvars-
        c = m.addVars(
            [(i, j, l) for i in N for h in K for j in J_h[h] for l in {h-1, h}.intersection(K_no_end)], name="c", vtype=GRB.CONTINUOUS, lb=0, ub=1
        )
        w = m.addVars([i for i in N], name="w", vtype=GRB.CONTINUOUS, lb=0, ub=1)
        x = m.addVars([j for j in J], name="x", vtype=GRB.CONTINUOUS)
        y = m.addVars([j for j in J], name="y", vtype=GRB.CONTINUOUS)
        b = m.addVars(
            [(i, h) for i in N for h in K_no_end], name="b", vtype=GRB.CONTINUOUS, lb=0, ub=20
        ) 
        delta = m.addVars(
            [(i, j, l) for i in N for h in K for j in J_h[h] for l in {h-1, h}.intersection(K_no_end)], name="delta", vtype=GRB.BINARY
        )
        lmbda = m.addVar(
            vtype=GRB.CONTINUOUS, name="lmbda", lb=0.5, ub=1
        )
        alpha = m.addVar(vtype=GRB.CONTINUOUS, name="alpha")
        self.b = b
        m.update() # maj
        
        # -------------------------------- Constaints -------------------------------- #
        # eq (7) in paper
        m.addConstrs(
            quicksum(c[i, j, h] for i in N) + x[j] + EPSILON == lmbda for h in K[:-1] for j in J_h[h] 
        )
        m.addConstrs(quicksum(c[i, j, h-1] for i in N) == lmbda + y[j] for h in K[1:] for j in J_h[h])
        m.addConstrs(alpha <= x[j] for j in J)
        m.addConstrs(alpha <= y[j] for j in J)
        # eq (6)
        m.addConstrs(c[i, j, l] <= w[i] for i in N for h in K for j in J_h[h] for l in {h-1, h}.intersection(K_no_end))
        m.addConstrs(c[i, j, l] <= delta[i, j, l] for i in N for h in K for j in J_h[h] for l in {h-1, h}.intersection(K_no_end))
        m.addConstrs(c[i, j, l] >= delta[i, j, l] - 1 + w[i] for i in N for h in K for j in J_h[h] for l in {h-1, h}.intersection(K_no_end))
        m.addConstrs(M * delta[i, j, l] + EPSILON >= g(i, j) - b[i, l] for i in N for h in K for j in J_h[h] for l in {h-1, h}.intersection(K_no_end))
        m.addConstrs(M * (delta[i, j, l] - 1) <= g(i, j) - b[i, l] for i in N for h in K for j in J_h[h] for l in {h-1, h}.intersection(K_no_end))
        m.addConstr(quicksum(w[i] for i in N) == 1)

        m.setObjective(alpha, GRB.MAXIMIZE)
        m.params.outputflag = self.verbose  # 0: no output, 1: display output
        self.model = m

    def solve(self, save_solution=True, error_rate = 0):
        # Résolution
        self.model.optimize()
        print(self.model.status)

        self.trained = True
        
        if save_solution:
            # Writing the solution in a file
            if not os.path.exists(os.path.dirname(self.sol_file)):
                os.makedirs(os.path.dirname(self.sol_file))
            self.model.write(self.sol_file)

    
    def get_solution(self, verbose=None):
        assert self.trained, "The model has not been trained yet"
        
        profiles = [] #[[]]
        weights = []
        lmbda = self.model.getVarByName("lmbda").x
        for i in range(self.n):
            weights.append(self.model.getVarByName("w[" + str(i) + "]").x)
        for h in range(self.p):
            profiles.append([])
            for i in range(self.n):
                profiles[h].append(self.model.getVarByName("b[" + str(i) + ","+ str(h+1) +"]").x)
        
        if verbose or (verbose == None and self.verbose):
            print("Solution :")
            print("**********")
            print("\t weights: ", weights)
            print("\t profiles: ", profiles)
            print("\t lmbda: ", lmbda)
            
        return profiles, weights, lmbda
    
    def predict(self, X: np.ndarray) -> list:
        assert self.trained, "The model has not been trained yet"
        
        predicted_classes = []
        profiles, weights, lmbda = self.get_solution(verbose = False)
        for row in X:
            predicted_classes.append(mr_sort(row, weights, profiles, lmbda)) # remove classe
        return predicted_classes