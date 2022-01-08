"""
This programme is used to solve the Inverse NCS problem.
Only binary classes (p = 1) are supported.
"""


import os
import pandas as pd
from sat import SATSolver
from config import data_saving_path, solution_saving_path, dimacs_saving_path, gophersat_path
from pyfiglet import Figlet


def inverse_ncs(
    data_file=data_saving_path,
    save_path=solution_saving_path,
    dimacs_saving_path=dimacs_saving_path,
    gophersat_path=gophersat_path,
    print_solution=True,
    save_solution=True,
):
    solver = SATSolver(data_file, save_path, dimacs_saving_path, gophersat_path, verbose=False)
    sol = solver.solve(save_solution=save_solution)
    if print_solution:
        print_sol(sol)
    return sol


def print_sol(sol):
    """
    Print the solution in a nice way
    """
    print("SAT solver result:")
    print("Satisfiable: " + str(sol["satisfiable"]))
    print(f"Resolution time: {sol['resolution_time']:.4f} seconds")
    print("\nLearnt sufficient coalitions:")
    for coalition, is_sufficient in sol["variables"].items():
        if len(coalition) > 1 and type(coalition[1]) != int:
            continue
        if is_sufficient:
            print("\t" + str(coalition))

    print("Learnt profiles intervals:")
    for b, interval in sol["profiles_intervals"].items():
        print(f"\t{b}: [{interval[0]:.2f}, {interval[1]:.2f}]")


if __name__ == "__main__":
    # clear console and print header
    os.system("cls" if os.name == "nt" else "clear")
    print(Figlet(font="slant").renderText("Inverse NCS"))

    inverse_ncs(print_solution=True, save_solution=True)

