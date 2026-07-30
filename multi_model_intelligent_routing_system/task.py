import asyncio

from celery_app import celery
from database.db import database
from .repo import RequestRepository
from .service import EvaluationService
from logger import get_logger

logger = get_logger(__name__)


@celery.task(name="evaluate_request")
def evaluate_request(request_id: int) -> None:
    logger.info(f"Received Celery task 'evaluate_request' for request_id: {request_id}")
    try:
        asyncio.run(run_evaluation(request_id))
        logger.info(f"Completed Celery task 'evaluate_request' for request_id: {request_id}")
    except Exception as e:
        logger.error(f"Error in Celery task 'evaluate_request' for request_id {request_id}: {e}", exc_info=True)
        raise


async def run_evaluation(request_id: int) -> None:
    async for session in database.get_session():
        service = EvaluationService(session)
        await service.evaluate(request_id)


@celery.task(name="retry_pending_evaluations")
def retry_pending_evaluations() -> None:
    logger.info("Starting retry_pending_evaluations task")

    try:
        asyncio.run(_retry_pending_evaluations())
        logger.info("Completed retry_pending_evaluations task")
    except Exception:
        logger.exception("Failed retry_pending_evaluations task")
        raise


async def _retry_pending_evaluations() -> None:
    async for session in database.get_session():
        repository = RequestRepository(session)
        service = EvaluationService(session)

        pending_requests = await repository.get_pending_evaluations()

        logger.info(
            "Found %s pending evaluations",
            len(pending_requests),
        )

        for request in pending_requests:
            try:
                logger.info(
                    "Evaluating request %s",
                    request.id,
                )

                await service.evaluate(request.id)

                logger.info(
                    "Finished evaluation for request %s",
                    request.id,
                )

            except Exception:
                logger.exception(
                    "Failed evaluation for request %s",
                    request.id,
                )