import numpy as np
import math
from munkres import Munkres
from matplotlib import pyplot as plt

from descriptor import compute_descriptor


def compute_cost(indexes, matrix):
    """ Compute Wasserstein distance from the flow  and the distance matrix """
    total = 0
    for row, columns in indexes:
        total += matrix[row][columns]
    return total

def distance_EMD(desc1, desc2, dist_function):
    """ Compute the flow with the min distance: the wasserstein distance """
    D = np.zeros((len(desc1), len(desc2)))
    for i in range(len(desc1)):
        for j in range(len(desc2)):
            D[i, j] = dist_function(desc1[i], desc2[j])

    m = Munkres()
    Dist_matrix = D.copy()
    indexes = m.compute(D)

    total_cost = compute_cost(indexes, Dist_matrix)
    return indexes, total_cost/len(desc1)

def dist_norm(a, b):
    a = np.array(a)
    b = np.array(b)
    return np.linalg.norm(a - b)

def compute_wasserstein_distance(set1, set2, dist_function=dist_norm, weights=None):
    """ Compute descriptors and then wasserstein distance between two set of signals """

    # Transform DataFrame pandas to numpy array
    arr1 = np.array(set1).T
    arr2 = np.array(set2).T

    # Compute list of descriptors
    desc1 = [compute_descriptor(s1) for s1 in arr1]
    desc2 = [compute_descriptor(s2) for s2 in arr2]

    if weights is not None and (len(weights) != len(compute_descriptor([0]))):
        print("lenght of weights and descriptors should be equal")
        return None

    if weights is not None:
        dist_class = DistWeights(weights)
        dist_function = dist_class.dist

    indexes, total_cost = distance_EMD(desc1, desc2, dist_function)

    return total_cost

class DistWeights(object):
    """docstring fos DistWeights"""
    def __init__(self, weights):
        self.weights = weights

    def dist(self, a, b):
        a = np.array(a)
        b = np.array(b)
        to_do_norm = [(a[i] - b[i]) * self.weights[i] for i in range(len(a))]

        return np.linalg.norm(to_do_norm)