import os

data_saving_path = os.path.join(os.path.dirname(__file__), "output/data.csv")
solution_saving_path = os.path.join(os.path.dirname(__file__), "output/solution.sol")
output_folder = os.path.join(os.path.dirname(__file__), "output/")

default_params = {
    "n": 6,  # Number of criteria
    "p": 1,  # number of profiles (the classe "no classe" is not counted)
    "profiles": [[10, 12, 10, 12, 8, 13]],  # b^h_j , h=1..p , j=1..n
    "weights": [0.15, 0.25, 0.1, 0.15, 0.1, 0.25],  # w_j , j=1..n
    "lmbda": 0.7,
    "n_generated": 1000,
}

default_params_2 = {
    "n": 10,  # Number of criteria
    "p": 1,  # number of profiles (the classe "no classe" is not counted)
    "profiles": [[10, 12, 10, 12, 8, 13, 11, 13, 14, 14]],  # b^h_j , h=1..p , j=1..n
    "weights": [0.08, 0.08, 0.08, 0.08, 0.08, 0.12, 0.10, 0.14, 0.14, 0.10],
    "lmbda": 0.8,
    "n_generated": 1000,
}

simple_default_params = {
    "n": 3,  # Number of criteria
    "p": 1,  # number of profiles (the classe "no classe" is not counted)
    "profiles": [[10, 12, 10]],  # b^h_j , h=1..p , j=1..n
    "weights": [0.3, 0.3, 0.4],
    "lmbda": 0.7,
    "n_generated": 100,
}

two_profiles_params = {
    "n": 4,  # Number of criteria
    "p": 2,  # number of profiles (the classe "no classe" is not counted)
    "profiles": [
        [10, 12, 10, 12],  # b^h_j , h=1..p , j=1..n
        [12, 14, 10, 13],
    ],
    "weights": [0.2, 0.2, 0.3, 0.3],
    "lmbda": 0.6,
    "n_generated": 500,
}


default_n_generated_list = [200, 400, 600, 800, 1000, 1500, 2000, 3000]
default_eval_rounds = 20
default_n_list = [2, 3, 4, 5, 6, 7]