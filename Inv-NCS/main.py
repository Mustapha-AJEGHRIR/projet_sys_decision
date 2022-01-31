"""
This file generates data for the Inverse NCS problem and then learns the solution.
"""
from learn import inverse_ncs
import config
from data_generator import generate_data
import os
from pyfiglet import Figlet

if __name__ == "__main__":
    # clear console and print header
    os.system("cls" if os.name == "nt" else "clear")
    print(Figlet(font="slant").renderText("Inverse NCS"))

    data = generate_data(config.params, balanced=True)

    inverse_ncs(solver_name="MaxSAT", data_file=data, print_solution=True, save_solution=True)

