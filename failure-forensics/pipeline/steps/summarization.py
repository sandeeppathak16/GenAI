from .base import BasePipelineStep
from ..schemas import (
    ClassificationResult,
    ExtractedEntities,
    SummaryResult,
    StepResult
)


class SummarizationStep(BasePipelineStep):

    output_model = SummaryResult

    step = "summarization"

    async def run(
        self,
        document: str,
        entities: ExtractedEntities,
        classification: ClassificationResult,
    ) -> StepResult[SummaryResult]:

        return await self.invoke(
            document=document,
            entities=entities,
            classification=classification,
        )

    def build_input(
        self,
        document: str,
        entities: ExtractedEntities,
        classification: ClassificationResult,
    ) -> str:

        return f"""
Document Type

{classification.document_type}


Extracted Entities

{entities.model_dump_json(indent=2)}


Document

{document}
"""