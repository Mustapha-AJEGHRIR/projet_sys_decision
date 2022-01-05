"""
This file generates the data for the Inverse MR-Sort problem.
"""
import pandas as pd
import numpy as np
import os
from instance_generation import get_instance
# from pyfiglet import Figlet
from tqdm import tqdm

def parameter_verification(weights: list[float], profiles: list[list[float]], lmbda: float, n:int, p:int) -> None:
    """
    Verifies if the parameters are correct.

    Arguments:
        weights: list(int) -- list of weights
        profiles: list(int) -- list of profiles
        lmbda: int -- lambda value
        n: int -- number of criterias
        p: int -- number of profiles
    Returns:
        bool -- True if the parameters are correct, False otherwise
    """
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


def generate(n_generated:int, weights: list[float], profiles: list[list[float]], lmbda: float) -> pd.DataFrame:
    """
    Generates the data for the Inverse MR-Sort problem.

    Arguments:
        n_generated: int -- number of generated students
        weights: list(int) -- list of weights
        profiles: list(int) -- list of profiles
        lmbda: int -- lambda value
    Returns:
        pd.DataFrame -- dataframe with the generated data
    """
    p = len(profiles)
    n = len(weights)
    data_list = []
    for _ in tqdm(range(n_generated)):
        instance = get_instance(weights, profiles, lmbda)
        data_list.append(instance)
    data = pd.DataFrame(data_list, columns=['mark_' + str(i+1) for i in range(n)]+['class'])   
    return data

def save_csv(df: pd.DataFrame, filename: str) -> None:
    """
    Save the dataframe to a csv file.
    """
    df.to_csv(filename, index=True)


if __name__ == "__main__":
    # clear console and print header
    # os.system('cls' if os.name == 'nt' else 'clear')
    # print(Figlet(font='slant').renderText('Inverse MR-Sort'))

    # Parameters
    n = 10  # Number of criteria
    p = 2 # number of profiles (the classe "no classe" is not counted)
    weights = [0.08, 0.08, 0.08, 0.08, 0.08, 0.12, 0.10, 0.14, 0.14, 0.10]
    profiles = [[10, 12, 10, 12, 8, 13, 11, 13, 14, 14], # b^h_j , h=1..p , j=1..n
                [12, 14, 10, 13, 9, 17, 13, 15, 17, 19]]
    lmbda = 0.6
    n_generated = 100
    
    parameter_verification(weights, profiles, lmbda, n, p)
    
    print("Generating data...")
    data = generate(n_generated, weights, profiles, lmbda)
    
    path = os.path.join(os.path.dirname(__file__) , "data.csv")
    print("Saving data to {}".format(path))
    save_csv(data, path)