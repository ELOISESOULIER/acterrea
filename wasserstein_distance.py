import numpy as np
import math
from munkres import Munkres
from matplotlib import pyplot as plt

def descriptor(V):
    """ Return a list of descriptors of the signal V """
    signal = abs(np.fft.fft(V))
    freq = np.fft.fftfreq(len(V))
    fr_max = freq[np.argmax(signal)]

    descriptors = [np.mean(V), np.std(V), np.min(V), np.max(signal)]
    descriptors.append(fr_max)

    return np.array(descriptors)

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
            D[i, j] = np.linalg.norm(desc1[i] - desc2[j])

    m = Munkres()
    Dist_matrix = D.copy()
    indexes = m.compute(D)

    total_cost = compute_cost(indexes, Dist_matrix)
    return indexes, total_cost/len(desc1)

def dist_norm(a, b):
    a = np.array(a)
    b = np.array(b)
    return np.linalg.norm(a - b)

def wasserstein_distance(set1, set2, dist_function=dist_norm):
    """ Compute descriptors and then wasserstein distance between two set of signals """
    desc1 = [descriptor(s1) for s1 in set1]
    desc2 = [descriptor(s2) for s2 in set2]

    indexes, total_cost = distance_EMD(desc1, desc2, dist_function)
    return total_cost