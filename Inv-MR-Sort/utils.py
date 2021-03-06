import numpy as np
from io import StringIO 
import sys
from config import quantization_factor

class Capturing(list):
    """
        For Academic licence, Gurobi spams us with warnings. lets make it quiet :D
    """
    def __enter__(self):
        self._stdout = sys.stdout
        sys.stdout = self._stringio = StringIO()
        return self
    def __exit__(self, *args):
        self.extend(self._stringio.getvalue().splitlines())
        del self._stringio  
        sys.stdout = self._stdout

def value_quantization(x :float) -> float : 
    return round(x * quantization_factor) / quantization_factor


def get_random_params(n_generated = 100,n=5, p=1, min_max = (0, 20)) -> dict:
    """
        Generates a random set of parameters. See config.py for an example.

    Args:
        n (int, optional): [number of criteria]. Defaults to 5.
        p (int, optional): [number of classes, p=1 means 2 classes, p+1 classes]. Defaults to 1.
        min_max (tuple, optional): [range of values for criteria]. Defaults to (0, 20).

    Returns:
        params [dict]: [randomly generated parameters]
    """
    params = {
        "n_generated": n_generated,
        "n": n,
        "p": p,
        "profiles": [],
        "weights": [],
        "lmbda": value_quantization(np.random.uniform(0.5, 1)),
    }
    for i in range(n):
        params['weights'].append(np.random.uniform(0, 1))
    weights_sum = sum(params['weights'])
    if weights_sum == 0: # like a Jackpot
        weights_sum = 1
        params['weights'][0] = 1
    for i in range(n): # Normalize weights to sumup to 1
        params["weights"][i] = value_quantization(params["weights"][i] / weights_sum)
    
    profiles_transpose = []
    for i in range(n):
        # Don't reach the bound of the range
        min_bound = (min_max[0] + min_max[1])/2 - (min_max[1] - min_max[0])/3
        max_bound = (min_max[0] + min_max[1])/2 + (min_max[1] - min_max[0])/3
        items_profiles = [np.random.uniform(min_bound, max_bound) for _ in range(p)]
        items_profiles.sort()
        profiles_transpose.append(items_profiles)
    for j in range(p):
        params['profiles'].append([value_quantization(profiles_transpose[i][j]) for i in range(n)])
    return params

def print_params(params: dict) -> None:
    """
        Prints the parameters.

    Args:
        params (dict): [parameters]
    """
    print("Parameters :")
    print("**********")
    print("\t n: {}".format(params['n']))
    print("\t p: {}".format(params['p']))
    print("\t weights: {}".format(params['weights']))
    print("\t profiles: {}".format(params['profiles']))
    print("\t lmbda: {}".format(params['lmbda']))
    print("\t n_generated: {}".format(params['n_generated']))
