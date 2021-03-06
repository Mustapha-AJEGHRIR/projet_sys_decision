"""
This file contains the functions that generate the instances.
"""

import numpy as np
import pandas as pd
from utils import value_quantization


def mr_sort_correction(
    data : pd.DataFrame, params: dict,
) -> pd.DataFrame:
    weights = params['weights']
    profiles = params['profiles']
    lmbda = params['lmbda']
    n_errors = 0
    corrected_data = data.copy()
    for i in range(len(data)):
        marks = data.iloc[i, :-1]
        _class = data.iloc[i, -1]
        real_class = mr_sort(marks, weights, profiles, lmbda)
        if real_class != _class:
            n_errors += 1
        corrected_data.iloc[i, -1] = real_class
    
    return corrected_data, n_errors



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
    weights: list[float], profiles: list[list[float]], lmbda: float, std=2, error_rate = 0
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
    marks = np.array(profile) + np.random.randn(len(profile)) * std
    marks =np.array(list( map(value_quantization, marks) ))
    marks = np.clip(marks, 0, 20)
    
    _class = mr_sort(marks, weights, profiles, lmbda)
    if error_rate > 0:
        if np.random.rand() < error_rate:
            _class = np.random.randint(0, len(profiles)+1)
    return list(marks) + [_class]
