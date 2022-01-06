"""
This programme is used to generate the data and solve the Inverse MR-Sort problem.
Only binary classes (p = 1) are supported.
"""



import os
import pandas as pd
from mip import MIPSolver
from data_generator import generate_save, generate
from config import simple_default_params, data_saving_path, solution_saving_path
from pyfiglet import Figlet
from utils import get_random_params, print_params
from eval import eval_parameters, plot_n_generated_effect



def inverse_mr_sort(data_path=data_saving_path, save_path=solution_saving_path):
    solver = MIPSolver(data_path, save_path, verbose = False)
    solver.solve()
    return solver.get_solution(verbose = True)
    


if __name__ == "__main__":
    # clear console and print header
    os.system('cls' if os.name == 'nt' else 'clear')
    print(Figlet(font='slant').renderText('Inverse MR-Sort'))
    path = data_saving_path
    
    generate_save(simple_default_params, verbose=False)
    print_params(simple_default_params)
    profiles, weights, lmbda = inverse_mr_sort()
    print("==================================================")
    
    eval_parameters(simple_default_params)
    
    plot_n_generated_effect(simple_default_params)
