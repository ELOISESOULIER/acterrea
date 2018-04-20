import numpy as np
import matplotlib.pyplot as plt
import pandas as pd


def load_data(data_file):
    """ Load simulated data from csv file """
    df = pd.read_csv(data_file)

    # Remove first column which is not a variable
    variables = [col for col in list(df.columns) if 'V' in col]
    df = df[variables]

    T, nb_sim = np.shape(df)
    print("Time horizon:", T)
    print("Number of simulations:", nb_sim)
    return nb_sim, T, df

def plot_data(df):
    """ Plot data simulated from lung model """
    variables = [col for col in list(df.columns) if 'V' in col]
    
    plt.figure()
    for col in variables:
        plt.plot(df[col])
    plt.title('O2 evolution on {} simulations'.format(len(variables)))
    plt.ylabel('O2')
    plt.xlabel('time')
    plt.show()