"""
Mixed integer linear program destined to select a particular feasible set of parameters
see parag 3 in: 
https://www.researchgate.net/publication/221367488_Learning_the_Parameters_of_a_Multiple_Criteria_Sorting_Method
"""

from gurobipy import read

class MIPSolver:
    def __init__(self, model_file='model.lp', sol_file="solution.sol"):
        self.model_file = model_file
        self.sol_file = sol_file

    def solve(self):
        self.model = read(self.model_file)
        self.model.params.outputflag = 0
        self.model.optimize()
        self.sol = self.model.getAttr('x', self.model.getVars())
        self.sol_file.write(str(self.sol))
        self.sol_file.close()
        return self.sol
