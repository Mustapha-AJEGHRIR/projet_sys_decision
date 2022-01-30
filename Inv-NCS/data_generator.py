"""
This file generates the data for the Inverse NCS problem.
"""

from collections import defaultdict
from unicodedata import category
import config
import pandas as pd
from tqdm import tqdm
import numpy as np
import os


def parse_from_dict(params):
    criteria, coalitions, profiles, n_generated = (
        params["criteria"],
        params["coalitions"],
        params["profiles"],
        params["n_generated"],
    )
    """
    Parses and validates the parameters from a dictionary.
    """
    n = len(criteria)

    assert n > 0, "Number of criteria must be greater than 0"
    assert n_generated > 0, "Number of generated instances must be greater than 0"
    for i, profile in enumerate(profiles):
        assert len(profile) == n, "Profile {} has {} criteria, but {} were specified".format(i + 1, len(profile), n)
    for h in range(1, len(profiles)):
        for i in range(n):
            assert (
                profiles[h][i] >= profiles[h - 1][i]
            ), "Profile {} has a higher frontier for criteria {} than profile {}".format(h + 1, i + 1, h)
    for coalition in coalitions:
        assert set(coalition).issubset(set(criteria)), "Coalition {} is not a subset of the criteria".format(coalition)
        assert len(coalition) > 0, "Coalition {} is empty".format(coalition)
        assert len(coalition) == len(set(coalition)), "Coalition {} has repeated criteria".format(coalition)
        for h in range(1, len(profiles)):
            assert all(
                profiles[h][i] >= profiles[h - 1][i] for i in coalition
            ), f"Profile {h + 1} has a lower frontier for criteria {coalition} than profile {h}"
            assert any(
                profiles[h][i] != profiles[h - 1][i] for i in coalition
            ), f"Profile {h + 1} has the same frontier for criteria {coalition} than profile {h}"

    return criteria, coalitions, profiles, n_generated


def ncs(marks, criteria, coalitions, profiles):
    """
    Returns the class of the instance by comparing to profiles
    see the paragraph "2.2. Non-compensatory sorting models" in:
        https://arxiv.org/pdf/1710.10098.pdf
    """
    for h, profile in enumerate(profiles):
        for i_coal, coalition in enumerate(coalitions):
            if any(marks[i] < profile[i] for i in coalition):  # failed coalition
                if i_coal == len(coalitions) - 1:  # no more coalitions
                    return h
            else:  # passed coalition
                break
    return h + 1


def generate_one(criteria, coalitions, profiles, std=2, mu=0.001):
    """
    Generates an instance (marks + class).

    Arguments:
        criteria: list(str) -- list of criteria
        coalitions: list(list(str)) -- list of coalitions
        profiles: list(list(int)) -- list of profiles
        std: int -- standard deviation of the noise
    Returns:
        list(int) -- list of marks and class for the instance
    """
    index = np.random.choice(range(len(profiles)))  # TODO: check if correct for case p > 1
    profile = profiles[index]
    marks = np.array(profile) + np.random.randn(len(profile)) * std
    marks = np.clip(marks, 0, 20)

    category = ncs(marks, criteria, coalitions, profiles)
    # add assignment errors
    if np.random.rand() < mu:
        category = np.random.choice( [c for c in [category - 1, category + 1] if 0 <= c < len(profiles)])
    return list(marks) + [category]


def generate_data(params: dict, verbose=False, balanced=True) -> pd.DataFrame:
    """
    Generates the data for the Inverse NCS problem.

    Arguments:
        params: dict -- parameters
        verbose: bool -- whether to print the progress
        balanced: bool -- whether to balance the classes
    Returns:
        pd.DataFrame -- dataframe with the generated data
    """
    if verbose:
        print("Verifying parameters...")
    criteria, coalitions, profiles, n_generated = parse_from_dict(params)
    n = len(criteria)
    data_list = []
    if balanced:
        counts = defaultdict(int)
    print("Generating data...")
    for _ in tqdm(range(n_generated)):
        instance = generate_one(criteria, coalitions, profiles)
        if balanced:
            while counts[instance[-1]] >= np.ceil(n_generated / (len(profiles) + 1)):
                instance = generate_one(criteria, coalitions, profiles)
            counts[instance[-1]] += 1
        data_list.append(instance)
    data = pd.DataFrame(data_list, columns=["criterion_" + str(i) for i in range(n)] + ["class"])
    if verbose:
        print("Classes generated:")
        for cls, count in sorted(counts.items()):
            print(f"\tClass {cls}: {count}")
        print()
    return data


if __name__ == "__main__":
    data = generate_data(config.params, balanced=True, verbose=True)

    # save data
    os.makedirs(os.path.dirname(config.data_saving_path), exist_ok=True)
    data.to_csv(config.data_saving_path, index=True)
