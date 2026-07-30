from typing import Optional
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from sqlalchemy.ext.asyncio import AsyncSession

from database.models.routing_system_model import RequestLog, Evaluation
from logger import get_logger

logger = get_logger(__name__)


class RequestRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        self,
        *,
        prompt: str,
        selected_model: str,
        response: str,
        latency: float,
        cost: float,
    ) -> RequestLog:
        logger.debug(f"Persisting request log for model: '{selected_model}'")

        request = RequestLog(
            prompt=prompt,
            selected_model=selected_model,
            response=response,
            latency_ms=latency,
            cost=cost,
        )

        self.session.add(request)
        await self.session.commit()
        await self.session.refresh(request)

        logger.debug(f"Persisted request log successfully (ID: {request.id})")
        return request

    async def get(self, request_id: int) -> Optional[RequestLog]:
        logger.debug(f"Fetching request log for ID: {request_id}")
        return await self.session.get(RequestLog, request_id)

    async def get_pending_evaluations(self) -> list[RequestLog]:
        stmt = (
            select(RequestLog)
            .outerjoin(Evaluation)
            .where(Evaluation.id.is_(None))
            .options(selectinload(RequestLog.evaluations))
        )

        result = await self.session.execute(stmt)
        return list(result.scalars().unique().all())


class EvaluationRepository:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        self,
        *,
        request_id: int,
        reference_model: str,
        reference_response: str,
        reference_latency_ms: float,
        reference_cost: float,
        judge_model: str,
        judge_latency_ms: float,
        judge_cost: float,
        winner: str,
        score: float,
        reason: str,
    ) -> Evaluation:
        logger.debug(f"Persisting evaluation log for request ID: {request_id}")
        evaluation = Evaluation(
            request_id=request_id,
            reference_model=reference_model,
            reference_response=reference_response,
            reference_latency_ms=reference_latency_ms,
            reference_cost=reference_cost,
            judge_model=judge_model,
            judge_latency_ms=judge_latency_ms,
            judge_cost=judge_cost,
            winner=winner,
            score=score,
            reason=reason,
        )

        self.session.add(evaluation)
        await self.session.commit()
        await self.session.refresh(evaluation)

        logger.debug(f"Persisted evaluation log successfully (ID: {evaluation.id})")
        return evaluation

    async def get_by_request_id(
        self,
        request_id: int,
    ) -> Optional[Evaluation]:
        logger.debug(f"Fetching evaluation log for request ID: {request_id}")
        return await self.session.scalar(
            select(Evaluation).where(
                Evaluation.request_id == request_id
            )
        )