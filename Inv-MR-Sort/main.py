"""
This programme is used to generate the data and solve the Inverse MR-Sort problem.
Only binary classes (p = 1) are supported.
"""


import os
import pandas as pd
from time import time
from pyfiglet import Figlet
from mip import MIPSolver
from data_generator import generate_save
from config import simple_default_params, default_params, data_saving_path, solution_saving_path
from utils import print_params
from eval import eval_parameters, plot_n_generated_effect_random, plot_n_effect_random


def inverse_mr_sort(data_path=data_saving_path, save_path=solution_saving_path):
    solver = MIPSolver(data_path, save_path, verbose = False)
    solver.solve()
    return solver.get_solution(verbose = True)
    


if __name__ == "__main__":
    # clear console and print header
    # os.system('cls' if os.name == 'nt' else 'clear')
    print(Figlet(font='slant').renderText('Inverse MR-Sort'))
    path = data_saving_path

    
    generate_save(default_params, verbose=False)
    print_params(default_params)
    
    tik = time()
    profiles, weights, lmbda = inverse_mr_sort()
    tok = time()
    print("Solving time: {:.2f}s".format(tok-tik))
    
    print("==================================================")
    eval_parameters(default_params)
    
    print("==================================================")
    plot_n_generated_effect_random(n=3, p=1)
    plot_n_effect_random(n_generated=1000, p=1)
    
