from .base import BasePipelineStep
from ..schemas import ClassificationResult, ExtractedEntities, StepResult


class ClassificationStep(BasePipelineStep):

    output_model = ClassificationResult

    step = "classification"

    async def run(
        self,
        document: str,
        entities: ExtractedEntities,
    ) -> StepResult[ClassificationResult]:
        return await self.invoke(
            document=document,
            entities=entities,
        )

    def build_input(
        self,
        document: str,
        entities: ExtractedEntities,
    ) -> str:

        return f"""
Document

{document}


Extracted Entities

{entities.model_dump_json(indent=2)}
"""