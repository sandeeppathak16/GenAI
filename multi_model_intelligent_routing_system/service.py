from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession


from .llm_registry import Router
from .request_handler import RequestHandler
from .model import CompletionRequest
from ..database.models.routing_system_model import RequestLog


class RequestRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        self,
        prompt: str,
        model: str,
        response: str,
        latency: float,
        cost: float,
    ) -> RequestLog:

        request = RequestLog(
            prompt=prompt,
            selected_model=model,
            response=response,
            latency_ms=latency,
            cost=cost,
        )

        self.session.add(request)

        await self.session.commit()

        await self.session.refresh(request)

        return request

    async def get(self, request_id: int) -> Optional[RequestLog]:
        return await self.session.get(RequestLog, request_id)


class CompletionService:

    def __init__(self, session):
        self.session = session
        self.rerequest_handler = RequestHandler()
        self.prompt_router = Router()

    async def complete(self, request: CompletionRequest):

        model = self.prompt_router.route(request.prompt)

        response = await self.request_handler.process_request(
            prompt=request.prompt,
            model_config=model,
        )

        repo = RequestRepository(self.session)
        request_log = await repo.create(
            prompt=request.prompt,
            model=model.name,
            response=response.content,
            latency=response.latency_ms,
            cost=response.cost,
        )


        return response