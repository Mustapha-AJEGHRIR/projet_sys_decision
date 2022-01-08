"""
This programme is used to solve the Inverse NCS problem.
Only binary classes (p = 1) are supported.
"""


import os
import pandas as pd
from sat import SATSolver
from config import simple_default_params, data_saving_path, solution_saving_path, dimacs_saving_path, gophersat_path
from pyfiglet import Figlet


def inverse_ncs(
    data_path=data_saving_path,
    save_path=solution_saving_path,
    dimacs_saving_path=dimacs_saving_path,
    gophersat_path=gophersat_path,
):
    solver = SATSolver(data_path, save_path, dimacs_saving_path, gophersat_path, verbose=False)
    sol = solver.solve()
    return sol


def print_sol(sol):
    """
    Print the solution in a nice way
    """
    print("SAT solver result: ")
    print("Satisfiable:", sol[0])
    print("Clauses:", sol[1])
    print("Learnt sufficient coalitions:")
    for coalition, is_sufficient in sol[2].items():
        if len(coalition) > 1 and type(coalition[1]) != int:
            continue
        if is_sufficient:
            print(coalition, end="\t")

    print()


if __name__ == "__main__":
    # clear console and print header
    os.system("cls" if os.name == "nt" else "clear")
    print(Figlet(font="slant").renderText("Inverse NCS"))

    sol = inverse_ncs()

    print_sol(sol)
