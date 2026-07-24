from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from .model import CompletionRequest
from ..database.dependencies import get_db
from .service import CompletionService


router = APIRouter()


@router.post("/v1/completions")
async def completion(
    request: CompletionRequest,
    session: Annotated[AsyncSession, Depends(get_db)],
):
    try:
        return CompletionService(session).complete()
    except Exception as e:
        raise