from .base import BasePipelineStep
from ..schemas import ExtractedEntities, StepResult


class EntityExtractionStep(BasePipelineStep):

    output_model = ExtractedEntities

    step = "entity_extraction"

    async def run(
        self,
        document: str,
    ) -> StepResult[ExtractedEntities]:
        return await self.invoke(document=document)

    def build_input(
        self,
        document: str,
    ) -> str:
        return document