import os


data_saving_path = os.path.join(os.path.dirname(__file__), "output/data.csv")
solution_saving_path = os.path.join(os.path.dirname(__file__), "output/solution.sol")


default_params = {
    "criteria": [0,1,2,3,4,5,6,7,8,9],  # N
    "coalitions": [[0,1,2,4], [3,4,5,0], [6,7,8], [9]], # B
    "profiles": [[10, 12, 10, 12, 8, 13, 11, 13, 14, 14]],  # b^h_j , h=1..p , j=1..n
    "n_generated": 1000,
}

simple_default_params = {
    "n": 3,  # Number of criteria
    "profiles": [[10, 12, 10]],  # b^h_j , h=1..p , j=1..n
    "n_generated": 100,
}

two_profiles_params = {
    "n": 10,  # Number of criteria
    "profiles": [
        [10, 12, 10, 12, 8, 13, 11, 13, 14, 14],  # b^h_j , h=1..p , j=1..n
        [12, 14, 10, 13, 9, 17, 13, 15, 17, 19],
    ],
    "n_generated": 1000,
}