from uuid import uuid4
from datetime import datetime, UTC

from sqlalchemy.ext.asyncio import AsyncSession
from .schemas import RunPipelineResponse, Trace
from .repository import TraceRepository
from .steps import EntityExtractionStep, ClassificationStep, SummarizationStep


class TraceService:

    def __init__(self, session):
        self.session = session

    async def start(self, document: str) -> Trace:
        return Trace(
            trace_id=str(uuid4()),
            started_at=datetime.now(UTC),
            status="running",
            document=document,
            spans=[],
            final_output=None,
            root_cause=None,
        )

    async def mark_success(
        self,
        trace: Trace,
        final_output: dict,
    ) -> None:
        trace.status = "success"
        trace.finished_at = datetime.now(UTC)
        trace.final_output = final_output

    async def mark_failed(
        self,
        trace: Trace,
        error: str,
    ) -> None:
        trace.status = "failed"
        trace.finished_at = datetime.now(UTC)
        trace.error = error


class PipelineService:
    def __init__(
        self,
        session: AsyncSession,
    ):
        self.session = session

        self.trace_service = TraceService(session)
        self.trace_repository = TraceRepository(session)

        self.entity_extractor = EntityExtractionStep()
        self.classifier = ClassificationStep()
        self.summarizer = SummarizationStep()

    async def run(self, document: str) -> RunPipelineResponse:
        trace = await self.trace_service.start(document)

        try:
            entities = await self.entity_extractor.run(
                document=document,
                trace=trace,
            )

            classification = await self.classifier.run(
                entities=entities,
                trace=trace,
            )

            summary = await self.summarizer.run(
                document=document,
                entities=entities,
                classification=classification,
                trace=trace,
            )

            trace.mark_success(summary)

            await self.trace_repository.save(trace)

            return RunPipelineResponse(
                trace_id=trace.id,
                status=trace.status,
                document_type=classification.document_type,
                summary=summary.summary,
            )

        except Exception as e:
            trace.mark_failed(str(e))
            await self.trace_repository.save(trace)
            raise