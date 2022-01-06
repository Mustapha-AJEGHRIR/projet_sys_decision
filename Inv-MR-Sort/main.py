import os
import pandas as pd
from mip import MIPSolver
from data_generator import generate_save
from config import simple_default_params, data_saving_path, solution_saving_path
from pyfiglet import Figlet


def inverse_mr_sort(data_path=data_saving_path, save_path=solution_saving_path):
    solver = MIPSolver(data_path, save_path)
    res = solver.solve()
    return res
    # print(res)


if __name__ == "__main__":
    # clear console and print header
    os.system('cls' if os.name == 'nt' else 'clear')
    print(Figlet(font='slant').renderText('Inverse MR-Sort'))
    
    
    path = data_saving_path

    data = generate_save(simple_default_params)

    inverse_mr_sort()
