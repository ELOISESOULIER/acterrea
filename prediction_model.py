""" Predicted models """


import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

class PredictionModel():
    def __init__(self, descriptors, tau, adjust_classes=True):
        self.descr = descriptors
        self.tau = tau
        
        self.adjust_classes = adjust_classes
        if adjust_classes:
            self.descr = self.adjust_size_classes()

    def adjust_size_classes(self):
        self.adjust_classes = True
        
        len_Y1 = np.sum(self.descr['Y'])
        len_Y0 = -np.sum([x - 1 for x in self.descr['Y']])

        descr1 = self.descr[self.descr['Y'] == 1]
        descr0 = self.descr[self.descr['Y'] == 0]
        indices = np.random.permutation(range(len(descr0)))

        if len_Y1 < len_Y0:
            new_descr0 = descr0.iloc[indices[:len_Y1]]
            new_descr1 = descr1
        else:
            new_descr0 = descr0
            new_descr1 = descr1.iloc[indices[:len_Y0]]
            
        print("The classes have been adjusted, there is now {} data in each class".format(len(new_descr0)))
        return pd.concat((new_descr0, new_descr1))
    
    def set_train_test_dataset_rand(self, list_descriptors, pct_test=0.2):
        X_data = np.array(self.descr[list_descriptors])
        Y_data = np.array(self.descr['Y_to_predict'])

        # Separate train / test
        nb_test = int(pct_test * len(X_data))
        print("{} data in the test set and {} in the train set".format(nb_test, len(X_data) - nb_test))
        indices = np.random.permutation(range(len(X_data)))

        self.X_test = X_data[indices[:nb_test]]
        self.Y_test = Y_data[indices[:nb_test]]

        self.X_train = X_data[indices[nb_test:]]
        self.Y_train = Y_data[indices[nb_test:]]
        
    def test_classif_model(self, model, print_results=False):
    
        self.regr_model = model
        self.regr_model.fit(self.X_train, self.Y_train)

        score_train = self.regr_model.score(self.X_train, self.Y_train)
        score_test = self.regr_model.score(self.X_test, self.Y_test)
        
        if print_results:
            print("Score on train set: {}%".format(round(score_train*100, 3)))
            print("Score on test set: {}%".format(round(score_test*100, 3)))
            
        return score_test, score_train
    
    def set_train_test_by_patient(self, list_descriptors, pct_test=0.3):
        if self.adjust_classes:
            print("To do training by patient do not adjust the classes. Load new data without adjusting the classes")
            return None
        
        nb_patient = len(np.unique(self.descr['trajec']))
        indices = np.random.permutation(range(nb_patient))
        
        # Test
        self.data_test = self.descr[self.descr['trajec'].isin(indices[:int(nb_patient*pct_test)])]
        self.X_test = self.data_test[list_descriptors]
        self.Y_test = self.data_test['Y']
        # Train
        self.data_train = self.descr[self.descr['trajec'].isin(indices[int(nb_patient*pct_test):])]
        self.X_train = self.data_train[list_descriptors]
        self.Y_train = self.data_train['Y']

        print("{} patients in the test set and {} in the train set".format(int(nb_patient*pct_test),
                                                                           nb_patient - int(nb_patient*pct_test)))

    def compute_metrics(self, model):
        
        _, _ = self.test_classif_model(model, print_results=False)
        
        y_predict = self.regr_model.predict(self.X_test)
        y_predict_df = pd.DataFrame({'y_predict': y_predict})
        y_predict_df = y_predict_df.reset_index()
        
        self.data_test = self.data_test.reset_index()
        data = pd.concat([self.data_test, y_predict_df], axis=1)
        
        # Pct of accident detected before the time of the accident
        prediction = {'id_patient': [], 'accident': [], 'time_of_accident': [],
                      'time_of_accident_tau': [], 'accident_tau': [],
                      'prediction': [], 'time_of_prediction': [],
                      'prediction_delay': []}
        
        patients = np.unique(self.data_test['trajec'])
        
        i = 0
        for n in patients:
            data_patient = data[data['trajec'] == n]
            
            prediction['id_patient'].append(n)
            prediction['accident'].append(np.sum(data_patient['Y']) != 0)
            prediction['accident_tau'].append(np.sum(data_patient['Y_to_predict']) != 0)  # Is there an accident to predict
            
            prediction['time_of_accident'].append(None)
            prediction['time_of_accident_tau'].append(None)
            prediction['prediction'].append(False)
            prediction['time_of_prediction'].append(None)
            prediction['prediction_delay'].append(None)


            # If there is an accident
            if prediction['accident_tau'][i]:
                y = [int(x) for x in list(data_patient['Y_to_predict'])]
                prediction['time_of_accident_tau'][i] = y.index(1)
                    
                if prediction['accident'][i]:
                    y = [int(x) for x in list(data_patient['Y'])]
                    prediction['time_of_accident'][i] = y.index(1)
                
                    # Prediction
                    is_predict = np.sum(data_patient['y_predict']) != 0
                    if is_predict:
                        y = [int(x) for x in list(data_patient['y_predict'])]
                        time_of_prediction = y.index(1)
                        prediction['time_of_prediction'][i] = time_of_prediction

                        if time_of_prediction < prediction['time_of_accident'][i]:
                            prediction['prediction'][i] = True
                            prediction['prediction_delay'][i] = time_of_prediction - prediction['time_of_accident_tau'][i]
            i += 1

        prediction = pd.DataFrame(prediction)
        return prediction
    
    def analyze_prediction(self, prediction, print_results=False):
        
        nb_accident = np.sum(prediction['accident_tau'])
        nb_prediction = np.sum(prediction['prediction'])
        
        nb_delay = len(prediction[prediction['prediction_delay'] > 0])
        nb_advance = len(prediction[prediction['prediction_delay'] < 0])
        nb_ok = len(prediction[prediction['prediction_delay'] == 0])
    
        avg_delay = np.mean(prediction[prediction['prediction_delay'] > 0]['prediction_delay'])
        avg_advance = -np.mean(prediction[prediction['prediction_delay'] < 0]['prediction_delay'])


        if print_results:
            print("\n-- METRICS --")
            print("Nb of patients having an accident:", nb_accident)
            print("{}% of them ({} patients) have been detected before the accident"
              .format(round(nb_prediction / nb_accident * 100, 2), nb_prediction))
            print("{}% of the detected accident where detected at tau (={}), {}% is advance and {}% with delay"\
                 .format(round(nb_ok / nb_prediction * 100, 2), self.tau, 
                         round(nb_advance / nb_prediction * 100, 2), round(nb_delay / nb_prediction * 100, 2)))
            print("{}% of the detected accident where detected at tau (={}), {}% is advance and {}% with delay"\
                 .format(round(nb_ok / nb_prediction * 100, 2), self.tau, 
                         round(nb_advance / nb_prediction * 100, 2), round(nb_delay / nb_prediction * 100, 2)))
            print("The average delay is {}, and the average advance is {}"\
                  .format(round(avg_delay, 2), round(avg_advance , 2)))

        return {'nb_accident': nb_accident, 'nb_prediction': nb_prediction,
                'nb_delay': nb_delay, 'nb_advance': nb_advance, 'nb_ok': nb_ok,
                'avg_delay': avg_delay, 'avg_advance': avg_advance} 