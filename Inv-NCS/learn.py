"""
This file is used to solve the Inverse NCS problem using data previously generated in `data_saving_path`.
"""


import os
import pandas as pd
from sat import SATSolver
from maxsat import MaxSATSolver
from config import data_saving_path, solution_saving_path, dimacs_saving_path, gophersat_path
from pyfiglet import Figlet


def inverse_ncs(
    solver_name="MaxSAT",
    data_file=data_saving_path,
    save_path=solution_saving_path,
    dimacs_saving_path=dimacs_saving_path,
    gophersat_path=gophersat_path,
    print_solution=True,
    save_solution=True,
):
    assert solver_name in ["MaxSAT", "SAT"], "Solver must be either MaxSAT or SAT"
    print(f"Learning the NCS model using {solver_name} Solver...")
    if solver_name == "MaxSAT":
        solver = MaxSATSolver(data_file, save_path, dimacs_saving_path, gophersat_path)
    elif solver_name == "SAT":
        solver = SATSolver(data_file, save_path, dimacs_saving_path, gophersat_path)
    sol = solver.solve(save_solution=save_solution)
    if print_solution:
        print_sol(sol, solver_name)
    return sol


def print_sol(sol, solver):
    """
    Print the solution in a nice way
    """
    print("\n********************")
    print(f"{solver} solver result:")
    print("Satisfiable: " + str(sol["satisfiable"]))
    print(f"Resolution time: {sol['resolution_time']:.4f} seconds")
    if solver == "MaxSAT":
        print(f"Number of correctly classified instances: {len(sol['correctly_classified'])}")
        print(f"Number of uncorrectly classified instances: {len(sol['uncorrectly_classified'])}")
        print(f"Uncorrectly classified instances: {sol['uncorrectly_classified']}")
    print("\nLearnt sufficient coalitions:")
    for coalition, levels in sol["sufficient_coalitions"].items():
        print(f"\t {coalition} at levels {levels}")
    print("\nLearnt profiles intervals:")
    for h, profile in enumerate(sol["profiles_intervals"]):
        print(f"\tProfile {h+1}: {[list(map(lambda d: round(d,2), l)) for l in profile]}")


if __name__ == "__main__":
    # clear console and print header
    os.system("cls" if os.name == "nt" else "clear")
    print(Figlet(font="slant").renderText("Inverse NCS"))

    inverse_ncs(solver_name="MaxSAT", print_solution=True, save_solution=True)

