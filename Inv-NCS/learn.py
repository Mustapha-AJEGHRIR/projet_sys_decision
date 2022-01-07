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


def print_params(params: dict) -> None:
    """
        Prints the parameters.

    Args:
        params (dict): [parameters]
    """
    print("Parameters :")
    print("**********")
    print("criteria :", params["criteria"])
    print("coalitions :", params["coalitions"])
    print("profiles :", params["profiles"])
    print("n_generated :", params["n_generated"])
    print("**********\n")


if __name__ == "__main__":
    # clear console and print header
    os.system("cls" if os.name == "nt" else "clear")
    print(Figlet(font="slant").renderText("Inverse NCS"))

    # print_params(simple_default_params)
    sol = inverse_ncs()
    print("\n")
