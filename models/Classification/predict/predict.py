import pickle

class Predict():
    def __init__(self, dataset):
        self.dataset = dataset
        self.result = None

    def predict(self):
        try:
            model = pickle.load(open('models\Classification\predict\classification.pkl', 'rb'))

            self.result = model.predict(self.dataset)[0]

            return self.result

        except:
            raise Exception