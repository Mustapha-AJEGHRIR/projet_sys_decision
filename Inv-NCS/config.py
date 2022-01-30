import os
import platform
import glob

data_saving_path = os.path.join(os.path.dirname(__file__), "output/data.csv")
solution_saving_path = os.path.join(os.path.dirname(__file__), "output/solution.sol")
solver_log_path = os.path.join(os.path.dirname(__file__), "output/solver_output.log")
dimacs_saving_path = os.path.join(os.path.dirname(__file__), "output/workingfile")
os_name = platform.system().lower().replace("windows", "win") + "64"
gophersat_dir = os.path.join(os.path.dirname(__file__), "gophersat", os_name)
gophersat_path = glob.glob(gophersat_dir + "/gophersat*")[0]

good_case_1 = {
    "criteria": [0, 1, 2, 3],  # N
    "coalitions": [[0], [1], [2], [3]],  # B
    "profiles": [[10, 10, 10, 10]],
    "n_generated": 128,
}
good_case_2 = {
    "criteria": [0, 1, 2, 3],
    "coalitions": [[0, 1], [2, 3]],
    "profiles": [[7.265, 10.1, 13.43, 17.789]],
    "n_generated": 128,
}
good_case_3 = {
    "criteria": [0, 1, 2, 3],
    "coalitions": [[0, 1], [2, 3]],
    "profiles": [[10, 10, 10, 10], [15, 10, 12, 10]],
    "n_generated": 128,
}

bad_case_1 = {
    "criteria": [0, 1, 2, 3],
    "coalitions": [[0], [1], [2]],  # sometimes gives [0,3] sufficient and profile b3 in [13.30, 13.32]
    "profiles": [[10, 10, 10, 10]],
    "n_generated": 128,
}

bad_case_2 = {
    "criteria": [0, 1, 2, 3],
    "coalitions": [[0, 1]],  # sometimes gives (0, 1, 2, 3) sufficient with very off b2 and b3 (around 4)
    "profiles": [[10, 10, 10, 10]],
    "n_generated": 128,
}
