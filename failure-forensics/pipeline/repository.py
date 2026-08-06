import json
from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession

from pipeline.schemas import Trace
from database.models import Trace as TraceModel


class TraceRepository:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def save(self, trace: Trace) -> None:
        db_trace = TraceModel(
            trace_id=trace.trace_id,
            status=trace.status,
            started_at=trace.started_at,
            finished_at=trace.finished_at,
        )

        self.session.add(db_trace)
        await self.session.commit()

        Path("traces").mkdir(exist_ok=True)

        file_path = Path("traces") / f"{trace.trace_id}.json"

        with open(file_path, "w") as f:
            json.dump(
                trace.model_dump(mode="json"),
                f,
                indent=2,
            )