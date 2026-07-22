from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split

from dataset import DatasetBuilder

import joblib

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PROMPTS_DIR = PROJECT_ROOT / "prompts"
CLASSIFIER_DIR = PROJECT_ROOT / "classifier"
MODEL_PATH = CLASSIFIER_DIR / "classifier.pkl"

df = DatasetBuilder().build(
    [
        PROMPTS_DIR / "simple.yaml",
        PROMPTS_DIR / "moderate.yaml",
        PROMPTS_DIR / "complex.yaml",
    ]
)

X = df.drop(columns=["label"])

y = df["label"]

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
)

classifier = RandomForestClassifier(
    random_state=42,
)

classifier.fit(
    X_train,
    y_train,
)

predictions = classifier.predict(X_test)

print(classification_report(y_test, predictions))

joblib.dump(
    classifier,
    MODEL_PATH,
)