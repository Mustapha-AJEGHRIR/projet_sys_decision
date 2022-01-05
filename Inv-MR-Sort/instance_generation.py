"""
This file contains the functions that generate the instances.
"""

import numpy as np


def mr_sort(
    marks: np.ndarray, weights: list[float], profiles: list[list[float]], lmbda: float
) -> int:
    """
    Returns the class of the instance by comparing to profiles
    see the paragraph "2.1 MR-Sort" in:
        https://hal.archives-ouvertes.fr/hal-01443088/document
    
    Arguments:
        marks: np.array(float) -- list of marks
        weights: list(int) -- list of weights
        profiles: list(int) -- list of profiles
        lmbda: int -- lambda value
    Returns:
        np.array(float) -- class of the instance
    """
    _class = 0
    for profile in profiles:
        sum_weights = 0
        for j, mark in enumerate(marks):
            if mark >= profile[j]:
                sum_weights += weights[j]
        if sum_weights < lmbda:
            break
        _class += 1
    return _class


def get_instance(
    weights: list[float], profiles: list[list[float]], lmbda: float, std=2
) -> list:
    """
    Generates an instance (marks + class).

    Arguments:
        weights: list(int) -- list of weights
        profiles: list(int) -- list of profiles
        lmbda: int -- lambda value
    Returns:
        list(int) -- list of marks and class for the instance
    """
    index = np.random.choice(range(len(profiles)))
    profile = profiles[index]
    marks = np.array(profile) + np.random.randn() * std
    _class = mr_sort(marks, weights, profiles, lmbda)
    return list(marks) + [_class]
