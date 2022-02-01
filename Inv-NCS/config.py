import os
import platform
import glob
import numpy as np

data_saving_path = os.path.join(os.path.dirname(__file__), "data/test_data.csv")
learning_data_path = os.path.join(os.path.dirname(__file__), "data/learning_data.csv")
solution_saving_path = os.path.join(os.path.dirname(__file__), "output/solution.sol")
solver_log_path = os.path.join(os.path.dirname(__file__), "output/solver_output.log")
dimacs_saving_path = os.path.join(os.path.dirname(__file__), "output/workingfile")
os_name = platform.system().lower().replace("windows", "win") + "64"
gophersat_dir = os.path.join(os.path.dirname(__file__), "gophersat", os_name)
gophersat_path = glob.glob(gophersat_dir + "/gophersat*")[0]


# eval params
default_n_generated_list = [32, 64, 256, 512]
default_n_list = [2, 3, 5, 7]
default_mu_list = [0., 0.01, 0.05, 0.1, 0.2]
default_eval_rounds = 1

params2 = {
    "criteria": list(range(3)),  # N
    "coalitions": [[0, 1], [2]],  # B
    "profiles": [[10, 10, 10], [11, 11, 11]],  # p=3
    "n_ground_truth": 1000,
    "n_learning_set": 128,
    "mu": 0.1,  # pourcentage of misclassified instances
}

params = {
    "criteria": list(range(9)),  # N
    "coalitions": [[0], [1], [2], [3], [4], [5], [6], [7], [8]],  # B
    "profiles": [[10, 10, 10, 10, 10, 10, 10, 10, 10], [11, 11, 11, 11, 11, 11, 11, 11, 11]],  # p=3
    "n_ground_truth": 1000,
    "n_learning_set": 128,
    "mu": 0.,  # pourcentage of misclassified instances
}


def get_random_params(n=9, p=3, n_learning_set=128, n_ground_truth=1000, min_max=(0, 20), mu=0.1) -> dict:
    """
        Generates a random set of parameters. See config.py for an example.

    Args:
        n (int, optional): [number of criteria]. Defaults to 5.
        p (int, optional): [number of classes, p=1 means 2 classes, p+1 classes]. Defaults to 1.
        min_max (tuple, optional): [range of values for criteria]. Defaults to (0, 20).

    Returns:
        params [dict]: [randomly generated parameters]
    """
    profiles =  np.array([np.random.choice(range(min_max[0]+1, min_max[1]), size=(p-1), replace=False) for _ in range(n)]).T
    profiles = np.sort(profiles,axis=0)
    
    params = {
        "criteria": list(range(n)),
        "coalitions": None,
        "profiles": profiles,
        "n_ground_truth": n_ground_truth,
        "n_learning_set": n_learning_set,
        "mu": mu,  # pourcentage of misclassified instances
    }
    # make a random set of coalitions
    params["coalitions"] = []
    while True:
        params["coalitions"].append(
            list(np.random.choice(params["criteria"], size=np.random.randint(1, n), replace=False))
        )
        if set([e for sublist in params["coalitions"] for e in sublist]) == set(params["criteria"]):
            break
    params["coalitions"] = [[i] for i in range(n)]
    return params