"""
This programme is used to generate the data and solve the Inverse MR-Sort problem.
Only binary classes (p = 1) are supported.
"""


import os
import argparse
import pandas as pd
from time import time
from pyfiglet import Figlet
from mip import MIPSolver
from data_generator import generate_save
from config import simple_default_params, default_params, two_profiles_params, data_saving_path, solution_saving_path
from utils import print_params, get_random_params
from eval import eval_parameters, plot_n_generated_effect_random, plot_n_effect_random


def inverse_mr_sort(data_path=data_saving_path, save_path=solution_saving_path, verbose=False):
    solver = MIPSolver(data_path, save_path, verbose = verbose)
    solver.solve()
    return solver.get_solution(verbose = True)
    


if __name__ == "__main__":
    # parse arguments
    parser = argparse.ArgumentParser(description='Use specific data')
    parser.add_argument('-d', '--data_path', type=str, default=None, help='path to the data')
    parser.add_argument('-l', '--light_mode', action='store_false', help='light mode, the full analysis will be skipped')
    parser.add_argument('-p', '--profiles',type=int, default=1, help='number of profiles')
    parser.add_argument('-n', '--n_criterias', type=int, default=5, help='number of criterias')
    parser.add_argument('-g', '--generate', type=int, default=None, help='number of generated data')
    args = parser.parse_args()
    
    # clear console and print header
    # os.system('cls' if os.name == 'nt' else 'clear')
    print(Figlet(font='slant').renderText('Inverse MR-Sort'))
    path = data_saving_path
    
    
    if args.generate is not None:
        assert args.generate > 0, "The number of generated data must be positive"
        assert args.profiles > 0, "The number of profiles must be positive"
        assert args.n_criterias > 0, "The number of items must be positive"
        
        print("Generating {} data Randomly for n = {} and p = {}".format(args.generate, args.n_criterias, args.profiles))
        params = get_random_params(args.generate, args.n_criterias, args.profiles)
    else :
        params = default_params

    
    if args.data_path == None:
        generate_save(params, verbose=False)
        print_params(params)
        
        tik = time()
        profiles, weights, lmbda = inverse_mr_sort()
        tok = time()
        print("Solving time: {:.2f}s".format(tok-tik))
        
        print("==================================================")
        eval_parameters(params)
        
        if not args.light_mode:
            print("==================================================")
            plot_n_generated_effect_random(n=3, p=1)
            plot_n_effect_random(n_generated=1000, p=1)
                    
    else :
        print("Using data from {}".format(args.data_path))
        print("Solving ...")
        tik = time()
        profiles, weights, lmbda = inverse_mr_sort(args.data_path, verbose=True)
        tok = time()
        print("Solving time: {:.2f}s".format(tok-tik))
    
