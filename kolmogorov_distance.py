import numpy as np
import pandas as pd
from scipy import stats

from descriptor import compute_descriptor


def nb_descriptors():
    """ Return the number of descriptors computed """
    a = np.zeros(100)
    d = compute_descriptor(a)
    return len(d)

def descriptor_matrix(df, nb_desc):
    
    nb_sim = df.shape[1]
    desc = np.zeros((nb_sim, nb_desc))
    var = [col for col in list(df.columns) if 'V' in col]
    
    for (idx, col) in enumerate(var):
        desc[idx, :] = compute_descriptor(df[col])
    
    return desc

def meanks(V1, V2):

    nb_desc = nb_descriptors()
    desc1 = descriptor_matrix(V1, nb_desc)
    desc2 = descriptor_matrix(V2, nb_desc)

    pvalues = np.zeros((nb_desc))    
    for i in range(0, nb_desc):
        [x, pvalues[i]] = stats.ks_2samp(desc1[:, i], desc2[:, i])

    return pvalues

def compute_kolmogorov_dist(V1, V2):
    pvalue = meanks(V1, V2)
    return np.mean(pvalue)