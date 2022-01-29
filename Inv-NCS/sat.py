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
import time


class SATSolver:
    def __init__(
        self,
        data_file=data_saving_path,
        sol_file=solution_saving_path,
        dimacs_file=dimacs_saving_path,
        gophersat_path=gophersat_path,
    ):
        self.sol_file = sol_file
        self.dimacs_file = dimacs_file
        self.gophersat_path = gophersat_path
        if type(data_file) == str:
            self.data = pd.read_csv(data_file, index_col=0)
        else:  # if data_file is a dataframe
            self.data = data_file

        self.i2v = None
        self.y_vars_start = None  # index of the first y variable
        self.n = None  # number of criteria
        self.build_model()

    def build_model(self):
        # Resolution of NCS
        # see paper https://www.researchgate.net/publication/354003148_Learning_Non-Compensatory_Sorting_models_using_efficient_SATMaxSAT_formulations
        # paragraph 4.1. A SAT formulation for Inv-NCS based on coalitions

        self.n = len(self.data.columns) - 1
        self.p = p = max(self.data["class"]) + 1  # = len(profiles) + 1

        criteria = range(self.n)

        # make all possible combinations of criteria of all lengths
        criteria_combinations = []
        for i in range(0, self.n + 1):
            criteria_combinations += list(combinations(range(self.n), i))

        # X[i] = list of marks of instance in criterion i;
        X = np.array([self.data.iloc[:, i] for i in criteria])

        counter = iter(range(1, X.size * p + len(criteria_combinations) * p + 1))
        # x[i,h,k] positive  means the mark k validates the criterion i wrt the profile b_h
        x = {}
        for i in criteria:
            for h in range(1, p):
                for k in X[i]:
                    if (i, h, k) not in x:
                        x[(i, h, k)] = next(counter)

        # y[B, h] positive if the coalition B is sufficient at level h
        y = {(B, h): next(counter) for B in criteria_combinations for h in range(1, p)}

        variables = list(x.keys()) + list(y.keys())
        v2i = {**x, **y}
        self.i2v = {v: k for k, v in v2i.items()}
        self.y_vars_start = len(x)

        C = lambda h: self.data.index[self.data["class"] == h]  # indexes of instances belonging to class h

        # if student validates a criterion i with evaluation k, then another student with criterion k'>k validates this criterion surely
        clauses_c1 = [
            [x[i, h, kp], -x[i, h, k]] for h in range(1, p) for i in criteria for k in X[i] for kp in X[i] if k < kp
        ]

        # if student validates a criterion i wrt the profile b_h', then he must validate the criterion i wrt the profile b_h (h < h')
        clauses_c2 = [
            [x[i, h, k], -x[i, hp, k]]
            for i in criteria
            for k in X[i]
            for h in range(1, p)
            for hp in range(1, p)
            if h < hp
        ]

        # if B is sufficient then each B' containing B is sufficient
        clauses_c3 = [
            [y[Bp, h], -y[B, h]]
            for h in range(1, p)
            for B in criteria_combinations
            for Bp in criteria_combinations
            if set(B).issubset(set(Bp)) and set(B) != set(Bp)
        ]

        # if B is sufficient at level hp then B is sufficient at level h < hp
        clauses_c4 = [
            [y[B, h], -y[B, hp]] for B in criteria_combinations for h in range(1, p) for hp in range(1, p) if h < hp
        ]

        # if a student is in class h-1 and validates all criteria (i,h) in B, then B is not sufficient
        clauses_c5 = []
        for h in range(1, p):
            for B in criteria_combinations:
                for u in C(h - 1):
                    clauses_c5.append([-y[B, h]] + [-x[i, h, X[i, u]] for i in B])

        # if a student is in class h and doesnt validate any criteria (i,h) in B, then complementary of B is sufficient
        clauses_c6 = []
        for h in range(1, p):
            for B in criteria_combinations:
                B_comp = tuple([i for i in criteria if i not in B])  # complementary
                for u in C(h):
                    clauses_c6.append([y[B_comp, h]] + [x[i, h, X[i, u]] for i in B])

        self.myClauses = clauses_c1 + clauses_c2 + clauses_c3 + clauses_c4 + clauses_c5 + clauses_c6

        self.myDimacs = self._clauses_to_dimacs(self.myClauses, len(variables))
        self._write_dimacs_file(self.myDimacs, self.dimacs_file)

    def solve(self, save_solution=True):
        # Start the solver
        sol = self._exec_gophersat(self.dimacs_file)

        # find profiles intervals
        profiles_intervals = [[[0, 20] for _ in range(self.n)] for _ in range(self.p - 1)]
        for var, is_satisfied in list(sol["variables"].items())[: self.y_vars_start]:
            criterion, h, mark = var
            if is_satisfied:  # marks validates criterion
                profiles_intervals[h - 1][criterion][1] = min(profiles_intervals[h - 1][criterion][1], mark)
            else:
                profiles_intervals[h - 1][criterion][0] = max(profiles_intervals[h - 1][criterion][0], mark)
        sol["profiles_intervals"] = profiles_intervals

        sol["sufficient_coalitions"] = {} # {B: [h where B is sufficient at level h]}
        for var, is_sufficient in list(sol["variables"].items())[self.y_vars_start :]:
            B, h = var
            if is_sufficient:
                if B in sol["sufficient_coalitions"]:
                    sol["sufficient_coalitions"][B].append(h)
                else:
                    sol["sufficient_coalitions"][B] = [h]

        if save_solution:
            print(f"Saving solution to {self.sol_file}")
            # Writing the solution in a file
            with open(self.sol_file, "w", newline="") as f:
                f.write("SAT solver result:\n")
                f.write("Satisfiable: " + str(sol["satisfiable"]) + "\n")
                f.write(f"Resolution time: {sol['resolution_time']:.4f} seconds\n")

                f.write("Learnt sufficient coalitions:" + "\n")
                for coalition, levels in sol["sufficient_coalitions"].items():
                    f.write(f"\t {coalition} at levels {levels}\n")

                f.write("Learnt profiles intervals:\n")
                for h, profile in enumerate(sol["profiles_intervals"]):
                    f.write(f"\tProfile {h+1}: {[list(map(lambda d: round(d,2), l)) for l in profile]}\n")

                # f.write("\nClauses: " + str(sol["clauses"]) + "\n")
                f.write("Satisfiable clauses: \n")
                for c in sol["variables"]:
                    f.write("\t" + str(c) + ": " + str(sol["variables"][c]) + "\n")

        return sol

    def _clauses_to_dimacs(self, clauses, numvar):
        dimacs = "c This is it\np cnf " + str(numvar) + " " + str(len(clauses)) + "\n"
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
        print(f"Solving with {cmd}...")
        start = time.time()
        result = subprocess.run([cmd, filename], stdout=subprocess.PIPE, check=True, encoding=encoding)
        delta_t = time.time() - start
        print(f"Solving took {delta_t:.4f} seconds")
        string = str(result.stdout)
        lines = string.splitlines()

        if lines[1] != "s SATISFIABLE":
            return {
                "satisfiable": False,
                "clauses": [],
                "variables": {},
                "resolution_time": delta_t,
            }

        model = lines[2][2:].split(" ")

        return {
            "satisfiable": True,
            "clauses": [int(x) for x in model if int(x) != 0],
            "variables": {self.i2v[abs(int(v))]: int(v) > 0 for v in model if int(v) != 0},
            "resolution_time": delta_t,
        }
