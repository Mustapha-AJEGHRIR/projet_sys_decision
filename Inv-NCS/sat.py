"""
Mixed integer linear program destined to select a particular feasible set of parameters
This solver works only for 2 classes (p = 1)
see parag 3 in: 
https://www.researchgate.net/publication/221367488_Learning_the_Parameters_of_a_Multiple_Criteria_Sorting_Method
"""

import numpy as np
import pandas as pd
import os
from config import solution_saving_path, data_saving_path, dimacs_saving_path, gophersat_path
import subprocess
from itertools import combinations


class SATSolver:
    def __init__(
        self,
        data_file=data_saving_path,
        sol_file=solution_saving_path,
        dimacs_file=dimacs_saving_path,
        gophersat_path=gophersat_path,
        epsilon=0.0000000001,
        M=100,
        verbose=False,
    ):
        self.sol_file = sol_file
        self.dimacs_file = dimacs_file
        self.gophersat_path = gophersat_path
        if type(data_file) == str:
            self.data = pd.read_csv(data_file, index_col=0)
        else:  # if data_file is a dataframe
            self.data = data_file
        self.model = None
        self.trained = False
        self.epsilon = epsilon
        self.M = M
        self.p = 1
        self.n = None
        self.verbose = verbose
        self.build_model()

    def build_model(self):

        n = len(self.data.columns) - 1
        criteria = range(n)

        # make all possible combinations of criteria of all lengths
        criteria_combinations = []
        for i in range(0, n + 1):
            criteria_combinations += list(combinations(range(n), i))

        # X[i] = list of marks of instance in criterion i;
        X = np.array([self.data.iloc[:, i] for i in criteria])

        # x[i,k] positive  means the student k validates the criterion i
        x = {(i, k): i*len(X[i])+i_k +
             1 for i in criteria for i_k, k in enumerate(X[i])}

        # y[B] positive if B is a sufficient coalition
        y = {v: i + 1 + len(x.keys())
             for i, v in enumerate(criteria_combinations)}

        variables = list(x.keys()) + list(y.keys())
        v2i = {**x, **y}
        self.i2v = {v: k for k, v in v2i.items()}
        A = self.data.index[self.data["class"] == 1]  # accepted instances
        R = self.data.index[self.data["class"] == 0]  # rejected instances

        # if student validates a criterion i with evaluation k, then another student with criterion k'>k validates this criterion surely
        clauses_2a = [[[x[i, kp], -x[i, k]] for k in X[i]
                       for kp in X[i] if k < kp] for i in criteria]
        clauses_2a = [item for sublist in clauses_2a for item in sublist] # flatten


        # clauses_2b = # TODO: case where p > 1

        # if B is sufficient then each B' caontaining B is sufficient
        clauses_2c = [[y[Bp], -y[B]]
                      for B in criteria_combinations for Bp in criteria_combinations if set(B).issubset(set(Bp)) and set(B) != set(Bp)]

        # if a student is accepted and validates all criteria i in B, then B is not sufficient
        clauses_2d = []
        for B in criteria_combinations:
            for u in R:
                clauses_2d.append([-y[B]]+[-x[i, X[i, u]] for i in B])

        # if an accepted student didn't validate any of B criteria, then tha complementary coalition of B is suffiscient
        clauses_2e = []
        for B in criteria_combinations:
            B_comp = tuple([i for i in criteria if i not in B]) # complementary
            for u in A:
                clauses_2e.append([y[B_comp]] + [x[i, X[i, u]] for i in B])

        self.myClauses = clauses_2a + clauses_2c + clauses_2d + clauses_2e

        self.myDimacs = self._clauses_to_dimacs(
            self.myClauses, len(variables))
        self._write_dimacs_file(self.myDimacs, self.dimacs_file)

    def solve(self, save_solution=True):
        # Start the solver
        res = self._exec_gophersat(self.dimacs_file)

        print("SAT solver result: ")
        print("Satisfiable:", res[0])
        print("Clauses:", res[1])
        print("Solution:", res[2])

        if save_solution:
            # Writing the solution in a file
            with open(self.sol_file, "w", newline="") as sol:
                sol.write("SAT solver result:\n")
                sol.write("Satisfiable: " + str(res[0]) + "\n")
                sol.write("Clauses: " + str(res[1]) + "\n")
                sol.write("Solution: \n")
                for c in res[2]:
                    sol.write("\t" + str(c) + ": " + str(res[2][c]) + "\n")

        return res

    def _clauses_to_dimacs(self, clauses, numvar):
        dimacs = "c This is it\np cnf " + \
            str(numvar) + " " + str(len(clauses)) + "\n"
        for clause in clauses:
            for atom in clause:
                dimacs += str(atom) + " "
            dimacs += "0\n"
        return dimacs

    def _write_dimacs_file(self, dimacs, filename):
        with open(filename, "w", newline="") as cnf:
            cnf.write(dimacs)

    def _exec_gophersat(self, filename, encoding="utf8"):
        cmd = self.gophersat_path
        result = subprocess.run(
            [cmd, filename], stdout=subprocess.PIPE, check=True, encoding=encoding)
        string = str(result.stdout)
        lines = string.splitlines()

        if lines[1] != "s SATISFIABLE":
            return False, [], {}

        model = lines[2][2:].split(" ")

        return (
            True,
            [int(x) for x in model if int(x) != 0],
            {self.i2v[abs(int(v))]: int(v) > 0 for v in model if int(v) != 0},
        )
