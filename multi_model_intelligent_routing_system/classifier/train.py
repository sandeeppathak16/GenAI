from pathlib import Path

from .dataset import DatasetBuilder
from .feedback_dataset_builder import FeedbackDatasetBuilder
from .trainer import ClassifierTrainer

from database.db import database


PROJECT_ROOT = Path(__file__).resolve().parent.parent

PROMPTS_DIR = PROJECT_ROOT / "prompts"

MODEL_DIR = PROJECT_ROOT / "classifier" / "models"


async def train():

    original_dataset = DatasetBuilder().build(
        [
            PROMPTS_DIR / "simple.yaml",
            PROMPTS_DIR / "moderate.yaml",
            PROMPTS_DIR / "complex.yaml",
        ]
    )

    async for session in database.get_session():

        feedback_dataset = (
            await FeedbackDatasetBuilder(
                session,
            ).build()
        )

    trainer = ClassifierTrainer(MODEL_DIR)

    trainer.train(
        datasets=[
            original_dataset,
            feedback_dataset,
        ]
    )


import asyncio

if __name__ == "__main__":
    asyncio.run(train())