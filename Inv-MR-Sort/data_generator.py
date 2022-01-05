"""
This file generates the data for the Inverse MR-Sort problem.

"""
import pandas as pd

def parameter_verification(weights: list(int), profiles: list(int), lmbda: int, n:int, p:int) -> bool:
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
    if len(weights) != p:
        return False
    if len(profiles) != n:
        return False
    if lmbda < 0:
        return False
    return True

def generate(n_generated:int, weights: list(int), profiles: list(int), lmbda: int) -> pd.DataFrame:
    """
    Generates the data for the Inverse MR-Sort problem.

    Arguments:
        n_generated: Number of generated instances.
        weights: list(int) -- list of weights
        profiles: list(int) -- list of profiles
        lmbda: int -- lambda value
    Returns:
        pd.DataFrame -- dataframe with the generated data
    """
    p = len(profiles)
    n = len(weights)
    data = pd.DataFrame(columns=['note', 'lmbda'])
    for student_id in range(n_generated):
        
        
    return 

def save_csv(df: pd.DataFrame, filename: str) -> None:
    """
    Save the dataframe to a csv file.
    """
    df.to_csv(filename, index=False)


if __name__ == "__main__":

    # Parameters
    n = 10  # Number of criteria
    p = 2 # number of profiles (the classe "no classe" is not counted)
    weights = [0.08, 0.08, 0.08, 0.08, 0.08, 0.12, 0.10, 0.14, 0.14, 0.10]
    profiles = [[10, 12, 10, 12, 8, 13, 11, 13, 14, 14],
                [12, 14, 10, 13, 9, 17, 13, 15, 17, 19]]
    lmbda = 0.6
    n_generated = 100
    # generate
    data = generate(n_generated, weights, profiles, lmbda)
    
    save_csv(data, "data.csv")
    