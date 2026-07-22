from dataclasses import asdict

import pandas as pd
import yaml

from feature_extractor import FeatureExtractor


class DatasetBuilder:

    def __init__(self):
        self.extractor = FeatureExtractor()

    def build(self, files):
        rows = []

        for file in files:
            with open(file) as f:
                data = yaml.safe_load(f)

            for prompt in data["prompts"]:

                features = self.extractor.extract(
                    prompt["prompt"]
                )

                row = asdict(features)

                row["label"] = prompt["tier"]

                rows.append(row)

        return pd.DataFrame(rows)