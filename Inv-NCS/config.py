import os
import platform
import glob

data_saving_path = os.path.join(os.path.dirname(__file__), "data/test_data.csv")
learning_data_path = os.path.join(os.path.dirname(__file__), "data/learning_data.csv")
solution_saving_path = os.path.join(os.path.dirname(__file__), "output/solution.sol")
solver_log_path = os.path.join(os.path.dirname(__file__), "output/solver_output.log")
dimacs_saving_path = os.path.join(os.path.dirname(__file__), "output/workingfile")
os_name = platform.system().lower().replace("windows", "win") + "64"
gophersat_dir = os.path.join(os.path.dirname(__file__), "gophersat", os_name)
gophersat_path = glob.glob(gophersat_dir + "/gophersat*")[0]

params = {
    "criteria": list(range(3)),  # N
    "coalitions": [[0, 1], [2]],  # B
    "profiles": [[10, 10, 10], [11, 11, 11]], # p=3
    "n_ground_truth": 1000,
    "n_learning_set": 128,
    "mu": 0.01, # pourcentage of misclassified instances
}

params2 = {
    "criteria": list(range(9)),  # N
    "coalitions": [[0], [1], [2], [3], [4], [5], [6], [7], [8]],  # B
    "profiles": [[10, 10, 10, 10, 10, 10, 10, 10, 10], [11, 11, 11, 11, 11, 11, 11, 11, 11]], # p=3
    "n_ground_truth": 1000,
    "n_learning_set": 128,
    "mu": 0.1, # pourcentage of misclassified instances
}
