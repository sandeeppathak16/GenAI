from typing import Optional
from dataclasses import asdict

from sqlalchemy import select

import pandas as pd

from database.models.routing_system_model import RequestLog, Evaluation
from .feature_extractor import FeatureExtractor


class FeedbackDatasetBuilder:
    def __init__(self, session):
        self.session = session
        self.feature_extractor = FeatureExtractor()

    async def build(self) -> pd.DataFrame:
        stmt = (
            select(RequestLog, Evaluation)
            .join(
                Evaluation,
                RequestLog.id == Evaluation.request_id,
            )
        )

        result = await self.session.execute(stmt)

        rows = []

        for request, evaluation in result.all():

            label = self._determine_label(
                request=request,
                evaluation=evaluation,
            )

            if label is None:
                continue

            features = self.feature_extractor.extract(
                request.prompt,
            )

            features = asdict(features)

            features["label"] = label

            rows.append(features)

        return pd.DataFrame(rows)

    def _determine_label(
        self,
        request: RequestLog,
        evaluation: Evaluation,
    ) -> Optional[str]:

        if (
            evaluation.winner == "candidate"
            and evaluation.score >= 0.8
        ):
            return self._model_to_label(
                request.selected_model
            )

        if (
            evaluation.winner == "reference"
            and evaluation.score <= 0.7
        ):
            return "complex"

        return None

    @staticmethod
    def _model_to_label(model: str) -> str:
        model = model.lower()

        if "mini" in model:
            return "simple"

        if "llama3" in model:
            return "moderate"

        return "complex"