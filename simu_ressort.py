import numpy as np
import matplotlib.pyplot as plt
import pickle
import itertools
import pandas as pd
import tqdm


def compute_ressort(T, dt, V_0, V_1, F, k, Vmin, Vmax, noise=False, sigma=0):
    """ Ressort perturbé
        d^2V(t)/dt^2 = -kV - F dV/dt
    """
    V = np.zeros((T, ))
    V[0] = V_0
    V[1] = V_1
    for t in range(2, T):
        V[t] = -dt**2*(k*V[t-1]) + 2*V[t-1] - V[t-2] - dt*F*(V[t-1] - V[t-2])
        
        if noise:
            V[t] += np.random.normal(0, sigma)
        if abs(V[t]) < Vmin:
            F = - F
        elif abs(V[t]) > Vmax:
            F = - F

    return V


def compute_N_ressort(N, F, k, Vmin, Vmax, T, dt, sigma=1):

    # On tire N simulations aléatoires selon un jeu de paramètre fixé. 
    # Seuls varient le bruit et les vitesses intiales

    simus = []

    for i in range(N):
        V_0 = np.random.random()*10 - 5
        V_1 = np.random.random()*10 - 5  

        V = compute_ressort(T, dt, V_0, V_1, F, k, Vmin, Vmax,
                            noise=True, sigma=sigma)
        simus.append(V)
        
    return np.array(simus)


def plot_ressort(V, F=None, k=None, Vmin=None, Vmax=None):
    """ Plot ressort """

    plt.plot(V)
    plt.ylabel("Position du ressort")
    plt.xlabel("t")
    if F and k and Vmax and Vmin:
        plt.title("F={}, k={}, Vmin={}, Vmax={}".format(F, k, Vmin, Vmax))
    elif F and k:
        plt.title("F={}, k={}".format(F, k))
    else:
        plt.title("Position du ressort au cours du temps")
    plt.show()


def save_obj(obj, name):
    """ Save an object in a pickle file """
    with open(name, 'wb') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)


def load_obj(name):
    """ Load the object from a pickle file """
    with open(name, 'rb') as f:
        return pickle.load(f)


def save_several_param_ressort(N, T, dt, list_k, list_F, list_Vmin, list_Vmax, path_save=None):
    """ Simuler N ressort poyr chaque jeu de parametres """

    all_simus = []

    for k, F, Vmin, Vmax in itertools.product(list_k, list_F, list_Vmin, list_Vmax):
        data = {'k': k, 'N': N, 'F': F, 'Vmin': Vmin, 'Vmax': Vmax}
        data['simu'] = compute_N_ressort(N, F, k, Vmin, Vmax, T, dt)
        all_simus.append(data)
                        
    print("{} jeux de parametres chargés".format(len(all_simus)))

    # Save
    if not path_save:
        path_save = "./data/ressort/simus.pkl"
    save_obj(all_simus, path_save)


def transform_simus_to_df(all_simus, nmax=None):
    """ Mettre les simus sous forme de DataFrame
        - nmax: nombre de simulations à transformer en DataFrame
    """
    
    if not nmax:  # Par defaut on met tout
        nmax = all_simus[0]['N']
        
    sets = []
    for simu in tqdm.tqdm(all_simus):
        df = pd.DataFrame(simu['simu'].T)  # .T pour transposee, on a pris la convention dans l'autre sens
        df.columns = ['V' + str(i) for i in range(simu['simu'].shape[0])]
        df = df[['V' + str(i) for i in range(nmax)]]
        sets.append(df)
    return sets