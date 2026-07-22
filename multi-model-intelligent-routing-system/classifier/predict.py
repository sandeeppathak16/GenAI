import joblib
import pandas as pd

from feature_extractor import FeatureExtractor


class PromptClassifier:

    def __init__(self):
        self.model = joblib.load(
            "classifier/classifier.pkl"
        )

        self.extractor = FeatureExtractor()

    def predict(self, prompt: str):

        features = self.extractor.extract(prompt)

        X = pd.DataFrame([features.__dict__])

        return self.model.predict(X)[0]