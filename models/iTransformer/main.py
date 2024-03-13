import torch
from models.iTransformer.experiments.exp_long_term_forecasting import Exp_Long_Term_Forecast

from models.iTransformer.args import Args

class ModelRunner:
    def __init__(self, dataset_dir_path, result_data_path, freq, features):
        self.dataset_dir_path = dataset_dir_path
        self.result_data_path = result_data_path
        self.freq = freq
        self.features = features
        self.args = Args(
            dataset_dir_path=self.dataset_dir_path,
            result_data_path=self.result_data_path,
            freq=self.freq,
            features=self.features
        )

    def run(self):
        try:
            exp = Exp_Long_Term_Forecast(self.args)
            return exp.predict()
            torch.cuda.empty_cache()
            return True
        except:
            raise Exception