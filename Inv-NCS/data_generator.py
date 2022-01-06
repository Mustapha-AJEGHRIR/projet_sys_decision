"""
This file generates the data for the Inverse NCS problem.
"""

from config import default_params
import pandas as pd


def parse_from_dict(params):
    criteria, coalitions, profiles, n_generated = params['criteria'], params['coalitions'], params['profiles'], params['n_generated']
    n = len(criteria)

    assert n>0, "Number of criteria must be greater than 0"
    assert n_generated>0, "Number of generated instances must be greater than 0"
    for i, profile in enumerate(profiles):
        assert len(profile) == n, "Profile {} has {} criteria, but {} were specified".format(i+1, len(profile), n)
    for h in range(1, len(profiles)):
        for i in range(n):
            assert profiles[h][i] >= profiles[h-1][i], "Profile {} has a higher frontier for criteria {} than profile {}".format(h+1, i+1, h)
    for coalition in coalitions:
        assert set(coalition).issubset(set(criteria)), "Coalition {} is not a subset of the criteria".format(coalition)
        assert len(coalition)>0, "Coalition {} is empty".format(coalition)

    return criteria, coalitions, profiles, n_generated
    

def generate(params: dict, verbose=False) -> pd.DataFrame:
    """
    Generates the data for the Inverse NCS problem.

    Arguments:
        params: dict -- parameters
    Returns:
        pd.DataFrame -- dataframe with the generated data
    """
    if verbose:
        print("Verifying parameters...")
    criteria, coalitions, profiles, n_generated = parse_from_dict(params)
    if verbose:
        print("Generating data...")
    p = len(profiles)
    data_list = []
    for _ in tqdm(range(n_generated)):
        instance = get_instance(weights, profiles, lmbda)
        data_list.append(instance)
    data = pd.DataFrame(data_list, columns=['mark_' + str(i+1) for i in range(n)]+['class'])   
    return data


if __name__=="__main__":
    generate(default_params)