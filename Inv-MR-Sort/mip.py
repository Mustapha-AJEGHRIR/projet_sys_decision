"""
Mixed integer linear program destined to select a particular feasible set of parameters
see parag 3 in: 
https://www.researchgate.net/publication/221367488_Learning_the_Parameters_of_a_Multiple_Criteria_Sorting_Method
"""

import numpy as np
import pandas as pd
from gurobipy import Model, GRB, quicksum
import os


class MIPSolver:
    def __init__(
        self,
        model_file="model.lp",
        data_file=os.path.join(os.path.dirname(__file__), "data.csv"),
        sol_file="solution.sol",
        epsilon=0.0000000001,
        M=100,
    ):
        self.model_file = model_file
        self.sol_file = sol_file
        self.data = pd.read_csv(data_file, index_col=0)
        self.model = None
        self.epsilon = epsilon
        self.M = M
        self.build_model()

    def build_model(self):
        m = Model("Mixed integer linear program")

        A_1 = pd.DataFrame(
            self.data["class"] == 0
        )  # The good class (named as in the paper)
        A_2 = pd.DataFrame(
            self.data["class"] == 1
        )  # The bad class (named as in the paper)
        J_1 = self.data.index[self.data["class"] == 0]
        J_2 = self.data.index[self.data["class"] == 1]
        J = range(len(self.data))
        n = len(self.data.columns) - 1
        N = I = range(n)
        EPSILON = self.epsilon
        M = self.M
        g = lambda i, j: self.data.iloc[j][
            "mark_" + str(i + 1)
        ]  # get mark of instance j in criteria i

        # Variables
        # https://support.gurobi.com/hc/en-us/community/posts/360077803892-Is-there-a-rule-to-write-addvar-or-addvars-
        c = m.addVars(
            [(i, j) for i in N for j in J], name="c", vtype=GRB.CONTINUOUS, lb=0, ub=1
        )
        w = m.addVars([i for i in N], name="w", vtype=GRB.CONTINUOUS, lb=0, ub=1)
        x = m.addVars([j for j in J], name="x", vtype=GRB.CONTINUOUS)
        y = m.addVars([j for j in J], name="y", vtype=GRB.CONTINUOUS)
        b = m.addVars(
            [i for i in N], name="b", vtype=GRB.CONTINUOUS, lb=0, ub=20
        )  # TODO: in paper b is fixed
        delta = m.addVars(
            [(i, j) for i in N for j in J], name="delta", vtype=GRB.BINARY
        )
        lmbda = m.addVar(
            vtype=GRB.CONTINUOUS, name="lmbda", lb=0.5, ub=1
        )  # TODO : check if the bounds are correct
        alpha = m.addVar(vtype=GRB.CONTINUOUS, name="alpha")

        # maj
        m.update()
        
        # Constaints
        # eq (7) in paper
        m.addConstrs(
            quicksum(c[i, j] for i in N) + x[j] + EPSILON == lmbda for j in J_1
        )
        m.addConstrs(quicksum(c[i, j] for i in N) == lmbda + y[j] for j in J_2)
        m.addConstrs(alpha <= x[j] for j in J)
        m.addConstrs(alpha <= y[j] for j in J)
        # eq (6)
        m.addConstrs(c[i, j] <= w[i] for i in N for j in J)
        m.addConstrs(c[i, j] <= delta[i, j] for i in N for j in J)
        m.addConstrs(c[i, j] >= delta[i, j] - 1 + w[i] for i in N for j in J)
        m.addConstrs(M * delta[i, j] + EPSILON >= g(i, j) - b[i] for i in N for j in J)
        m.addConstrs(M * (delta[i, j] - 1) <= g(i, j) - b[i] for i in N for j in J)
        m.addConstr(quicksum(w[i] for i in N) == 1)

        m.setObjective(alpha, GRB.MAXIMIZE)

        m.params.outputflag = 0  # 0: no output, 1: display output
        self.model = m

    def solve(self):
        # Résolution
        self.model.optimize()

        # Priting the optimal solutions obtained
        print("Optimal solution:")
        for v in self.model.getVars():
            print(v.varName, v.x)

        # Writing the solution in a file
        self.model.write(self.sol_file)
        return self.model.objVal
