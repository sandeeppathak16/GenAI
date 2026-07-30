from pathlib import Path
import re
import joblib
import pandas as pd

from .feature_extractor import FeatureExtractor


class PromptClassifier:

    def __init__(self):
        self.extractor = FeatureExtractor()

        self.model = joblib.load(
            self._latest_model_path()
        )

    def predict(self, prompt: str):
        features = self.extractor.extract(prompt)

        X = pd.DataFrame([features.__dict__])

        return self.model.predict(X)[0]

    def _latest_model_path(self):
        model_dir = Path(
            "multi_model_intelligent_routing_system/classifier/models"
        )

        models = []

        for file in model_dir.glob("classifier_v*.pkl"):
            match = re.search(
                r"classifier_v(\d+)\.pkl",
                file.name,
            )

            if match:
                models.append(
                    (
                        int(match.group(1)),
                        file,
                    )
                )

        if not models:
            raise FileNotFoundError(
                "No classifier models found."
            )

        return max(models, key=lambda x: x[0])[1]