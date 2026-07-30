from .llm_registry import Router
from .request_handler import RequestHandler
from .model import CompletionRequest, QualityTier, EvaluationResult
from .repo import RequestRepository, EvaluationRepository
from .llm_registry import EVALUATION_MODEL, get_highest_quality_model
from .evaluation_prompt import build_evaluation_prompt
from logger import get_logger

logger = get_logger(__name__)


class CompletionService:

    def __init__(self, session):
        self.session = session
        self.request_handler = RequestHandler()
        self.prompt_router = Router()
        self.request_repository = RequestRepository(session)

    async def complete(self, request: CompletionRequest):
        logger.info("Routing completion request...")
        routed_model = self.prompt_router.route(request.prompt)
        logger.info(f"Routed prompt to model: '{routed_model.display_name}' (Tier: {routed_model.quality_tier.value})")

        response = await self.request_handler.process_request(
            prompt=request.prompt,
            model_config=routed_model,
        )

        request_log = await self.request_repository.create(
            prompt=request.prompt,
            selected_model=routed_model.display_name,
            response=response.text,
            latency=response.latency_ms,
            cost=response.cost,
        )
        logger.info(f"Created request log in database with ID: {request_log.id}")

        if routed_model.quality_tier != QualityTier.HIGH:
            logger.info(f"Dispatching background evaluation task for request ID: {request_log.id}")
            from .task import evaluate_request
            evaluate_request.delay(request_log.id)
        else:
            logger.info(f"Skipping background evaluation for high tier model: '{routed_model.display_name}'")

        return response


class EvaluationService:

    def __init__(self, session):
        self.request_handler = RequestHandler()
        self.request_repo = RequestRepository(session)
        self.evaluation_repo = EvaluationRepository(session)
        self.reference_model = get_highest_quality_model()
        self.evaluation_model = EVALUATION_MODEL

    async def evaluate(self, request_id: int):
        logger.info(f"Starting evaluation for request ID: {request_id}")
        request = await self.request_repo.get(request_id)

        if request is None:
            logger.warning(f"Evaluation aborted: Request ID {request_id} not found in database.")
            return

        logger.info(f"Processing reference request using model: '{self.reference_model.display_name}'")
        reference_response = await self.request_handler.process_request(
            prompt=request.prompt,
            model_config=self.reference_model,
        )

        evaluation_prompt = build_evaluation_prompt(
            prompt=request.prompt,
            candidate=request.response,
            reference=reference_response.text,
        )

        logger.info(f"Processing judge evaluation using model: '{self.evaluation_model.display_name}'")
        judge_response = await self.request_handler.process_request(
            prompt=evaluation_prompt,
            model_config=self.evaluation_model,
        )

        result = EvaluationResult.model_validate_json(
            judge_response.text
        )

        evaluation = await self.evaluation_repo.create(
            request_id=request.id,
            reference_model=self.reference_model.display_name,
            reference_response=reference_response.text,
            reference_latency_ms=reference_response.latency_ms,
            reference_cost=reference_response.cost,
            judge_model=self.evaluation_model.display_name,
            judge_latency_ms=judge_response.latency_ms,
            judge_cost=judge_response.cost,
            winner=result.winner,
            score=result.score,
            reason=result.reason,
        )
        logger.info(
            f"Evaluation saved for request ID {request.id} | "
            f"Winner: {result.winner} | Score: {result.score} | Reason: {result.reason}"
        )
        return evaluation