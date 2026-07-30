from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from .model import CompletionRequest
from database.dependencies import get_db
from .service import CompletionService
from logger import get_logger

logger = get_logger(__name__)

router = APIRouter()


@router.post("/v1/completions")
async def completion(
    request: CompletionRequest,
    session: Annotated[AsyncSession, Depends(get_db)],
):
    logger.info(f"Received completion request (prompt len={len(request.prompt)}): {request.prompt[:50]!r}...")
    try:
        response = await CompletionService(session).complete(request=request)
        logger.info(
            f"Successfully processed request | Model: {response.model} | "
            f"Latency: {response.latency_ms:.2f}ms | Cost: ${response.cost:.6f}"
        )
        return response
    except Exception as e:
        logger.error(f"Error processing completion request: {e}", exc_info=True)
        raise