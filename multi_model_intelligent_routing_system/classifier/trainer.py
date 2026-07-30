from pathlib import Path
import re
import joblib
import pandas as pd

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report


class ClassifierTrainer:

    def __init__(self, model_dir: Path):
        self.model_dir = model_dir
        self.model_dir.mkdir(parents=True, exist_ok=True)

    def train(self, datasets: list[pd.DataFrame]) -> Path:
        df = pd.concat(datasets, ignore_index=True)

        X = df.drop(columns=["label"])
        y = df["label"]

        X_train, X_test, y_train, y_test = train_test_split(
            X,
            y,
            test_size=0.2,
            random_state=42,
            stratify=y,
        )

        classifier = RandomForestClassifier(
            random_state=42,
        )

        classifier.fit(X_train, y_train)

        predictions = classifier.predict(X_test)

        print(classification_report(y_test, predictions))

        output_path = self._next_model_path()

        joblib.dump(classifier, output_path)

        print(f"Saved classifier to {output_path}")

        return output_path

    def _next_model_path(self) -> Path:
        versions = []

        for file in self.model_dir.glob("classifier_v*.pkl"):
            match = re.search(r"classifier_v(\d+)\.pkl", file.name)

            if match:
                versions.append(int(match.group(1)))

        version = max(versions, default=0) + 1

        return self.model_dir / f"classifier_v{version}.pkl"