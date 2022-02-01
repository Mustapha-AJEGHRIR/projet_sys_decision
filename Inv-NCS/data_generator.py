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
    """
    Parses and validates the parameters from a dictionary.
    """
    criteria, coalitions, profiles, n_ground_truth, n_learning_set, mu = (
        params["criteria"],
        params["coalitions"],
        params["profiles"],
        params["n_ground_truth"],
        params["n_learning_set"],
        params["mu"],
    )
    n = len(criteria)

    assert n > 0, "Number of criteria must be greater than 0"
    assert n_ground_truth > 0 and n_learning_set > 0, "Number of generated instances must be greater than 0"
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

    return criteria, coalitions, profiles, n_ground_truth, n_learning_set, mu


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


def generate_one(criteria, coalitions, profiles, std=2):
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
    return list(marks) + [category]


def generate_data(params: dict, verbose=False, balanced=True, save=True) -> [pd.DataFrame, pd.DataFrame]:
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
    criteria, coalitions, profiles, n_ground_truth, n_learning_set, mu = parse_from_dict(params)
    if verbose:
        print("Generating ground truth data...")
    test_data = _generate_data(criteria, coalitions, profiles, n_ground_truth, verbose=verbose, balanced=balanced)
    if save:
        # save test_data
        os.makedirs(os.path.dirname(config.data_saving_path), exist_ok=True)
        test_data.to_csv(config.data_saving_path, index=True)

    if verbose:
        print("Generating learning set data...")
    learning_data = _generate_data(criteria, coalitions, profiles, n_learning_set, verbose=verbose, balanced=balanced)
    correct_learning_data = learning_data.copy()
    learning_data["is_mistake"] = False
    # add assignment mistakes
    mistakes_indexes = np.random.choice(range(len(learning_data)), size=int(len(learning_data) * mu), replace=False)
    for i in mistakes_indexes:
        category = np.random.choice(
            [
                c
                for c in [learning_data.iloc[i]["class"] - 1, learning_data.iloc[i]["class"] + 1]
                if 0 <= c < len(profiles)
            ]
        )
        learning_data.loc[i, "class"] = int(category)
        learning_data.loc[i, "is_mistake"] = True
    learning_data["class"] = learning_data["class"].astype(int)
    if verbose:
        print("Number of mistakes:", len(mistakes_indexes))
    if save:
        os.makedirs(os.path.dirname(config.learning_data_path), exist_ok=True)
        learning_data.to_csv(config.learning_data_path, index=True)
    return test_data, learning_data, correct_learning_data


def _generate_data(criteria, coalitions, profiles, n_generated, verbose, balanced):
    n = len(criteria)
    data_list = []
    if balanced:
        counts = defaultdict(int)
    for _ in tqdm(range(n_generated), disable=not verbose):
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
    data, learning_data, _ = generate_data(config.params, balanced=True, verbose=True, save=True)

