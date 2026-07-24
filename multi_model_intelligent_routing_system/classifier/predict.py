import joblib
import pandas as pd

from multi_model_intelligent_routing_system.classifier.feature_extractor import FeatureExtractor


class PromptClassifier:

    def __init__(self):
        self.model = joblib.load(
            "multi_model_intelligent_routing_system/classifier/classifier.pkl"
        )

        self.extractor = FeatureExtractor()

    def predict(self, prompt: str):

        features = self.extractor.extract(prompt)

        X = pd.DataFrame([features.__dict__])

        return self.model.predict(X)[0]