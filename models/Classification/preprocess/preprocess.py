import pickle
import talib
from talib import abstract
import pandas as pd
import numpy as np

class Preprocess():
    def __init__(self, dataset):
        self.dataset = dataset
        self.index_features = []
        self.problem_count = 0
        self.threshold_dict = {
                'Temperature (°C)': [20, 33],
                'Humidity (%)': [50, 60],
                'Daya (watt)': [60, 80],
                'Light Lux (meter)': [100, 120],
                'Availability (Uptime)': [131.62967291359942, 142.36469061725444],
                'Network Latency (ms)': [42.08074924821079, 45.58052781508361],
                'Availibility (Uptime)': [130, 143],
                'Network Lattency (ms)': [40, 1000]
            }

    def _apply_labels(self, row, col_length, threshold_dict):
        problem = 0
        for i in range(col_length):
            if row.iloc[i] < threshold_dict[row.index[i]][0] or row.iloc[i] > threshold_dict[row.index[i]][1]:
                problem += 1


        return problem

    def _feature_labelling(self):
        self.dataset["problem_count"] = self.dataset.apply(lambda x: self._apply_labels(x, len(self.dataset.columns), self.threshold_dict), axis=1)

        return True

    def _get_ema(self):
        temp = pd.DataFrame()
        for i in range(len(self.dataset.columns)):
            temp[self.dataset.columns[i]] = talib.abstract.EMA(self.dataset.iloc[:, i], timeperiod = 48)
        self.dataset = temp.iloc[-1]

        self.problem_count = 0
        for i in range(len(self.dataset) - 1):
            if self.dataset.iloc[i] < self.threshold_dict[self.dataset.index[i]][0] or self.dataset.iloc[i] > self.threshold_dict[self.dataset.index[i]][1]:
                self.index_features.append(i)
                self.problem_count += 1
        self.dataset['problem_count'] = self.problem_count

        return True     

    def _scaler(self):
        
        scaler = pickle.load(open("models\Classification\Preprocess\scaler.pkl", 'rb'))
        self.dataset = scaler.transform(np.array(self.dataset).reshape(1, -1))

        return True
    
    def preprocess(self):
        try:
            self._feature_labelling()
            self._get_ema()
            self._scaler()
            
            return self.dataset, self.index_features, self.problem_count
        
        except:
            raise Exception