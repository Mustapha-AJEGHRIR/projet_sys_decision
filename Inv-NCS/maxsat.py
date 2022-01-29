"""
Mixed integer linear program destined to select a particular feasible set of parameters
This solver works only for 2 classes (p = 1)
see parag 3 in: 
https://www.researchgate.net/publication/221367488_Learning_the_Parameters_of_a_Multiple_Criteria_Sorting_Method
"""

import numpy as np
import pandas as pd
import os
from config import solution_saving_path, data_saving_path, dimacs_saving_path, gophersat_path, solver_log_path
import subprocess
from itertools import combinations
import time


class MaxSATSolver:
    def __init__(
        self,
        data_file=data_saving_path,
        sol_file=solution_saving_path,
        dimacs_file=dimacs_saving_path,
        gophersat_path=gophersat_path,
    ):
        self.sol_file = sol_file
        self.solver_log_file = solver_log_path
        self.dimacs_file = dimacs_file + ".wcnf"
        self.gophersat_path = gophersat_path
        if type(data_file) == str:
            self.data = pd.read_csv(data_file, index_col=0)
        else:  # if data_file is a dataframe
            self.data = data_file

        self.i2v = None
        self.n = None  # number of criteria
        self.build_model()

    def build_model(self):
        # Resolution of NCS
        # see paper https://www.researchgate.net/publication/354003148_Learning_Non-Compensatory_Sorting_models_using_efficient_SATMaxSAT_formulations
        # paragraph 5.1. A MaxSAT relaxation for Inv-NCS based on coalitions

        self.n = len(self.data.columns) - 1
        self.p = p = max(self.data["class"]) + 1  # = len(profiles) + 1

        criteria = range(self.n)

        # make all possible combinations of criteria of all lengths
        criteria_combinations = []
        for i in range(0, self.n+1):
            criteria_combinations += list(combinations(range(self.n), i))

        # X[i] = list of marks in criterion i;
        X = np.array([self.data.iloc[:, i] for i in criteria])

        counter = iter(range(1, X.size * (p-1) + len(criteria_combinations) * (p-1) + len(self.data.index) + 1))
        # x[i,h,k] positive  means the mark k validates the criterion i wrt the profile b_h
        self.x = x = {}
        for i in criteria:
            for h in range(1, p):
                for k in X[i]:
                    if (i, h, k) not in x:
                        x[(i, h, k)] = next(counter)

        # y[B, h] positive if the coalition B is sufficient at level h
        self.y = y = {(B, h): next(counter) for B in criteria_combinations for h in range(1, p)}

        # z[u] positive if u is correctly classified
        self.z = z = {u: next(counter) for u in self.data.index}

        variables = list(x.keys()) + list(y.keys()) + list(z.keys())
        v2i = {**x, **y, **z}
        self.i2v = {v: k for k, v in v2i.items()}

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
        clauses_c5_ = []
        for h in range(1, p):
            for B in criteria_combinations:
                for u in C(h - 1):
                    clauses_c5_.append([-y[B, h], -z[u]] + [-x[i, h, X[i, u]] for i in B])

        # if a student is in class h and doesnt validate any criteria (i,h) in B, then complementary of B is sufficient
        clauses_c6_ = []
        for h in range(1, p):
            for B in criteria_combinations:
                B_comp = tuple([i for i in criteria if i not in B])  # complementary
                for u in C(h):
                    clauses_c6_.append([y[B_comp, h], -z[u]] + [x[i, h, X[i, u]] for i in B])

        # maximize number of correctly classified instances(=alternative)
        clauses_goal = [[z[u]] for u in self.data.index]

        self.myClauses = clauses_c1 + clauses_c2 + clauses_c3 + clauses_c4 + clauses_c5_ + clauses_c6_ + clauses_goal
        self.w_max = self.data.size + 1
        w1 = 1
        self.weights = [self.w_max] * (len(self.myClauses) - len(clauses_goal)) + [w1] * len(clauses_goal)

        self.myDimacs = self._clauses_to_dimacs(self.myClauses, self.weights, len(variables))
        self._write_dimacs_file(self.myDimacs, self.dimacs_file)

    def solve(self, save_solution=True):
        # Start the solver
        sol = self._exec_gophersat(self.dimacs_file)

        # find profiles intervals
        profiles_intervals = [[[0, 20] for _ in range(self.n)] for _ in range(self.p - 1)]
        for var, is_satisfied in list(sol["variables"].items())[: len(self.x)]:
            criterion, h, mark = var
            if is_satisfied:  # marks validates criterion
                profiles_intervals[h - 1][criterion][1] = min(profiles_intervals[h - 1][criterion][1], mark)
            else:
                profiles_intervals[h - 1][criterion][0] = max(profiles_intervals[h - 1][criterion][0], mark)
        sol["profiles_intervals"] = profiles_intervals

        sol["sufficient_coalitions"] = {} # {B: [h where B is sufficient at level h]}
        for var, is_sufficient in list(sol["variables"].items())[len(self.x) :len(self.x) + len(self.y)]:
            B, h = var
            if is_sufficient:
                if B in sol["sufficient_coalitions"]:
                    sol["sufficient_coalitions"][B].append(h)
                else:
                    sol["sufficient_coalitions"][B] = [h]

        sol["correctly_classified"] = [] # indexes of correctly classified instances
        sol["uncorrectly_classified"] = [] # indexes of incorrectly classified instances
        for var, is_correctly_classified in list(sol["variables"].items())[len(self.x) + len(self.y) :]:
            u = var
            if is_correctly_classified:
                sol["correctly_classified"].append(u)
            else:
                sol["uncorrectly_classified"].append(u)

        if save_solution:
            print(f"Saving solution to {self.sol_file}")
            # Writing the solution in a file
            with open(self.sol_file, "w", newline="") as f:
                f.write("MaxSAT solver result:\n")
                f.write("Satisfiable: " + str(sol["satisfiable"]) + "\n")
                f.write(f"Resolution time: {sol['resolution_time']:.4f} seconds\n")

                f.write(f"Number of correctly classified instances: {len(sol['correctly_classified'])}\n")
                f.write(f"Number of uncorrectly classified instances: {len(sol['uncorrectly_classified'])}\n")
                f.write(f"Uncorrectly classified instances: {sol['uncorrectly_classified']}\n")

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

    def _clauses_to_dimacs(self, clauses, weights, numvar):
        # Convert a list of clauses to a DIMACS format
        # more info: http://www.maxsat.udl.cat/08/index.php?disp=requirements
        dimacs = "c This is it\np wcnf " + str(numvar) + " " + str(len(clauses)) + "\n"
        # dimacs = "c This is it\np wcnf " + str(numvar) + " " + str(len(clauses)) + " " + str(self.w_max) + "\n"
        for clause, w in zip(clauses, weights):
            dimacs += str(w) + " " + " ".join(map(str, clause)) + " 0\n"
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
        with open(self.solver_log_file, "w", newline="") as f:
            f.write(string)
        lines = string.splitlines()

        if lines[2] != "s OPTIMUM FOUND":
            return {
                "satisfiable": False,
                "variables": {},
                "resolution_time": delta_t,
            }

        variables = lines[3][2:].split(" ")
        variables = [int(x.replace("x", "")) for x in variables if x != ""]
        return {
            "satisfiable": True,
            "variables": {self.i2v[abs(v)]: v > 0 for v in variables},
            "resolution_time": delta_t,
        }
