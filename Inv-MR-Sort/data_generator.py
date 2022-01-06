"""
This file generates the data for the Inverse MR-Sort problem.
"""
import pandas as pd
import numpy as np
import os
from instance_generation import get_instance

from tqdm import tqdm
from config import default_params, data_saving_path

def parameter_verification(weights: list[float], profiles: list[list[float]], lmbda: float, n:int, p:int, n_generated: int) -> None:
    """
    Verifies if the parameters are correct.

    Arguments:
        weights: list(int) -- list of weights
        profiles: list(int) -- list of profiles
        lmbda: int -- lambda value
        n: int -- number of criterias
        p: int -- number of profiles
        n_generated: int -- number of generated items
    Returns:
        bool -- True if the parameters are correct, False otherwise
    """
    assert n_generated > 0, "The number of generated items must be greater than 0."
    assert n>0, "n must be positive"
    assert p>0, "p must be positive"
    assert len(weights) == n, "The number of weights must be equal to the number of criterias n"
    assert len(profiles) == p, "The number of given profiles must be equal to the number of profiles p"
    for i, profile in enumerate(profiles):
        assert len(profile) == n, "The number of bounds in profile {} must be equal to the number of criterias n".format(i)
    assert lmbda >= 0 and lmbda <=1, "The lambda value must be between 0 and 1"
    for h in range(1, len(profiles)):
        for i in range(n):
            assert profiles[h][i] >= profiles[h-1][i], "The bounds of profile {} must be greater than the bounds of profile {}".format(h, h-1)


def save_csv(df: pd.DataFrame, filename: str) -> None:
    """
    Save the dataframe to a csv file.
    """
    df.to_csv(filename, index=True)

def parse_from_dict(params: dict) -> tuple:
    """
    Parses the parameters from a dictionary.

    Arguments:
        params: dict -- parameters
    Returns:
        tuple -- tuple with the parameters
    """
    n = params['n']
    p = params['p']
    profiles = params['profiles']
    weights = params['weights']
    lmbda = params['lmbda']
    n_generated = params['n_generated']
    parameter_verification(weights, profiles, lmbda, n, p, n_generated)
    return n, p, profiles, weights, lmbda, n_generated
    
    
def generate(params: dict, verbose=False) -> pd.DataFrame:
    """
    Generates the data for the Inverse MR-Sort problem.

    Arguments:
        params: dict -- parameters
    Returns:
        pd.DataFrame -- dataframe with the generated data
    """
    if verbose:
        print("Verifying parameters...")
    n, p, profiles, weights, lmbda, n_generated = parse_from_dict(params)
    if verbose:
        print("Generating data...")
    p = len(profiles)
    n = len(weights)
    data_list = []
    # for _ in tqdm(range(n_generated)):
    for _ in range(n_generated):
        instance = get_instance(weights, profiles, lmbda)
        data_list.append(instance)
    data = pd.DataFrame(data_list, columns=['mark_' + str(i+1) for i in range(n)]+['class'])   
    return data

def generate_save(params: dict, verbose=False):
    """
    Generates the data for the Inverse MR-Sort problem and saves it to a csv file.
    """
    data = generate(params, verbose)
    if verbose:
        print("Saving data to {}".format(data_saving_path))
    save_csv(data, data_saving_path)

if __name__ == "__main__":
    # Generating
    generate_save(default_params)
    