""" Model to load the data, compute the Y variable to predict and the descriptors """


import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


def plot_two_scales_y(plot1, plot2, title='', x_label='', y_label1='', y_label2='', label1='', label2=''):
    """ Plot two curves with different Y-axis """
    fig, ax1 = plt.subplots()
    
    ax1.set_xlabel(x_label)
    ax1.set_ylabel(y_label1)
    ax1.plot(plot1, color='b', label=label1)
    ax1.legend()
    
    ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis

    ax2.set_ylabel(y_label2)  # we already handled the x-label with ax1
    ax2.plot(plot2, color='r', label=label2)
    ax2.legend()
    
    fig.tight_layout()  # otherwise the right y-label is slightly clipped
    plt.title(title)
    plt.show()


class DescriptorModel():
    """ Model to load the data, compute the Y variable to predict and the descriptors """
    def __init__(self, data_file):
        self.df = pd.read_csv(data_file)
        self.T, self.nb_sim = np.shape(self.df)
        self.nb_sim -= 1
        print("{} simulations with {} values loaded".format(self.nb_sim, self.T))
        
        self.variables = [col for col in list(self.df.columns) if 'V' in col]
        
    def plot_some_simulations(self, nb=20):
        
        plt.figure()
        for col in self.variables[:nb]:
            plt.plot(self.df[col])
        plt.title('Evolution on {} simulations'.format(nb))
        plt.xlabel('time')
        plt.show()
        
    def process_var(self, params):
        """ Compute Y variable to be predicted """
        self.params = params
        
        # Concatenate x variable, and compute the cumulative mean
        X = []
        trajec = []
        X_cummean = []

        for j in range(len(self.variables)):
            col = self.variables[j]
            X += list(self.df[col])
            trajec += [j for _ in range(len(self.df))]  # Trajec = the number of the trajectory

            # CumMean of X (t-1 previous values)
            cummean = np.cumsum(self.df[col]) / np.array(range(1, len(self.df) + 1))
            X_cummean += [self.df[col][0]] + list(cummean[:-1])

        self.data = pd.DataFrame({'X': X, 'trajec': trajec, 'X_cummean': X_cummean})

        # Compute Y
        self.data['X_diff'] = abs(self.data['X'] - self.data['X_cummean'])
        # The difference between X and the cummean is it below the threshold thres_mean ?
        self.data['Y1'] = self.data['X_diff'].apply(lambda x: 1 if x > params['thres_mean'] else 0)
        # The value of X is it below the general threshold thres_gal ?
        self.data['Y2'] = self.data['X'].apply(lambda x: 1 if abs(x - params['X0_base']) > params['thres_gal'] else 0)

        # The incident happens if one of the two previous event happen
        self.data['Y'] = self.data['Y1'] + self.data['Y2']
        self.data['Y'] = self.data['Y'].apply(lambda x: 1 if x > 0 else 0)
        
    def compute_descriptors(self, tau, len_X):
        """Separate data x in windows of lenght len_X
           and compute descriptors on this window  """
        
        self.tau = tau
        self.len_X = len_X
        
        try:
            self.data
        except:
            print("First process the variables using the function 'process_var' with parameters")

        descriptors = {'X': [], 'Y': [], 'trajec': [], 'Y_to_predict': [],
                       'mean': [],
                       'diff_to_mean': [],
                       'diff_first_second_mean': [],
                       'diff_to_X0': [],
                       'actual_evolution': [], 'past_evolution': [], 'mean_past_evolution': []}
        
        for i in range(1, len_X + 1):
            descriptors['X_{}'.format(i)] = []

        for n in range(self.nb_sim):
            for j in range(len_X, self.T - tau):
                i = n*self.T + j
                X_ = list(self.data['X'][i - len_X:i])  # Past

                descriptors['X'].append(self.data['X'][i])
                descriptors['Y'].append(self.data['Y'][i])
                descriptors['Y_to_predict'].append(self.data['Y'][i + tau])
                descriptors['trajec'].append(self.data['trajec'][i])
                
                descriptors['mean'].append(np.mean(X_))
                descriptors['diff_to_mean'].append(np.abs(self.data['X'][i] - np.mean(X_)))
                descriptors['diff_first_second_mean'].append(np.abs(np.mean(X_[:int(len_X/2)])\
                                                                    - np.mean(X_[int(len_X/2):])))
                descriptors['diff_to_X0'].append(np.abs(np.mean(X_) - self.params['X0_base']))
                descriptors['actual_evolution'].append(self.data['X'][i] - self.data['X'][i-1])

                past_evolution = [X_[k] - X_[k-1] for k in range(1, len(X_))]
                descriptors['past_evolution'].append(past_evolution)
                descriptors['mean_past_evolution'].append(np.mean(past_evolution))


                # Past values
                for k in range(1, len_X + 1):
                    descriptors['X_{}'.format(k)].append((self.data['X'][i - k]))

        self.descriptors = pd.DataFrame(descriptors)

        self.name_descriptors = list(descriptors.keys())
        self.name_descriptors.remove('X')
        self.name_descriptors.remove('Y')
        self.name_descriptors.remove('trajec')
        self.name_descriptors.remove('Y_to_predict')
        print("The descriptors computed are:", self.name_descriptors)
        print("{} trajectories of length {}".format(self.nb_sim, self.T))