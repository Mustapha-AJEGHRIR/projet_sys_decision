"""
This file generates data for the Inverse NCS problem and then learns the solution.
"""
from learn import inverse_ncs
from config import default_params, data_saving_path
from data_generator import generate_data
import os
from pyfiglet import Figlet

if __name__ == "__main__":
    # clear console and print header
    os.system("cls" if os.name == "nt" else "clear")
    print(Figlet(font="slant").renderText("Inverse NCS"))

    data = generate_data(default_params, balanced=True)

    # save data
    os.makedirs(os.path.dirname(data_saving_path), exist_ok=True)
    data.to_csv(data_saving_path, index=True)

    inverse_ncs(data, print_solution=True, save_solution=True)
