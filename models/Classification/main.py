import pandas as pd
from models.Classification.preprocess.preprocess import Preprocess
from models.Classification.predict.predict import Predict

class ModelRunner:
    def __init__(self, dataset_dir_path):
        self.dataset_dir_path = dataset_dir_path
        self.result = None

    def run(self):
        try:
            data = pd.read_csv(self.dataset_dir_path)
            data.set_index('date', inplace=True)

            PreprocessClass = Preprocess(data)
            data, index_features = PreprocessClass.preprocess()
            amount = len(index_features)

            PredictClass = Predict(data)
            label = PredictClass.predict()

            self.result = {
                'amount': amount,
                'index_features': index_features,
                'label' : label
            }

            return self.result
        except:
            raise Exception
    