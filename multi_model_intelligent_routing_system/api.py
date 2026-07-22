from fastapi import APIRouter

from llm_registry import Router
from request_handler import RequestHandler
from model import CompletionRequest

router = APIRouter()

request_handler = RequestHandler()
prompt_router = Router()


@router.post("/v1/completions")
async def completion(request: CompletionRequest):

    model = prompt_router.route(request.prompt)

    response = await request_handler.process_request(
        prompt=request.prompt,
        model_config=model,
    )

    return response