import joblib
import pandas as pd

from multi_model_intelligent_routing_system.classifier.feature_extractor import FeatureExtractor
from logger import get_logger

logger = get_logger(__name__)


class PromptClassifier:

    def __init__(self):
        self.model = joblib.load(
            "multi_model_intelligent_routing_system/classifier/classifier.pkl"
        )
        self.extractor = FeatureExtractor()

    def predict(self, prompt: str):
        logger.debug("Extracting features for prompt classification...")
        features = self.extractor.extract(prompt)

        X = pd.DataFrame([features.__dict__])

        prediction = self.model.predict(X)[0]
        logger.debug(f"Classifier output tier: '{prediction}'")
        return prediction