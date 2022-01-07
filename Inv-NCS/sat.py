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

        A_1 = pd.DataFrame(self.data["class"] == 0)  # The good class (named as in the paper)
        A_2 = pd.DataFrame(self.data["class"] == 1)  # The bad class (named as in the paper)
        J_1 = self.data.index[self.data["class"] == 0]
        J_2 = self.data.index[self.data["class"] == 1]
        J = range(len(self.data))
        self.n = n = len(self.data.columns) - 1
        N = I = range(n)
        EPSILON = self.epsilon
        M = self.M
        g = lambda i, j: self.data.iloc[j]["mark_" + str(i + 1)]  # get mark of instance j in criteria i

        # Exemple # TODO: had exemple khess lalla asmae t9addu
        # Ensemble V
        Vertices = ["A", "B", "C", "D"]

        # Ensemble E
        Edges = [("A", "B"), ("A", "C"), ("B", "C"), ("B", "D")]

        # k=3
        Colors = [1, 2, 3]

        # Clauses
        # Définitions des variables
        variables = [(i, j) for i in Vertices for j in Colors]

        # Création des dictionnaires
        v2i = {v: i + 1 for i, v in enumerate(variables)}  # numérotation qui commence à 1
        self.i2v = {i: v for v, i in v2i.items()}

        clauses_atleastonecolor = [[v2i[i, j] for j in Colors] for i in Vertices]
        clauses_differentcolors = [[-v2i[v1, k], -v2i[v2, k]] for k in Colors for v1, v2 in Edges]
        clauses_atmostonecolor = [[-v2i[i, j1], -v2i[i, j2]] for i in Vertices for j1, j2 in combinations(Colors, 2)]
        self.myClauses = clauses_atleastonecolor + clauses_atmostonecolor + clauses_differentcolors

        self.myDimacs = self._clauses_to_dimacs(self.myClauses, len(variables))
        self._write_dimacs_file(self.myDimacs, self.dimacs_file)

    def solve(self, save_solution=True):
        # Lancer la résolution
        res = self._exec_gophersat(self.dimacs_file)

        # Résultat
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
        result = subprocess.run([cmd, filename], stdout=subprocess.PIPE, check=True, encoding=encoding)
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

