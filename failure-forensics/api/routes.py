from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from database.dependencies import get_db
from logger import get_logger
from pipeline.schemas import (
    RunPipelineRequest,
    RunPipelineResponse,
)
from pipeline.service import PipelineService

logger = get_logger(__name__)

router = APIRouter(prefix="/pipeline", tags=["Pipeline"])


@router.post(
    "/v1/run",
    response_model=RunPipelineResponse,
)
async def run_pipeline(
    request: RunPipelineRequest,
    session: Annotated[AsyncSession, Depends(get_db)],
):
    logger.info("Received pipeline execution request")

    try:
        result = await PipelineService(session).run(
            document=request.document,
        )

        logger.info(
            "Pipeline completed successfully | "
            f"Trace={result.trace_id} "
            f"Status={result.status}"
        )

        return result

    except Exception as exc:
        logger.exception("Pipeline execution failed")

        raise HTTPException(
            status_code=500,
            detail="Pipeline execution failed.",
        ) from exc