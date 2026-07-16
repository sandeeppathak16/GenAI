import asyncio
from pathlib import Path
from typing import Optional

import yaml

from llm_registry import MODEL_REGISTRY
from request_handler import RequestHandler

CONCURRENCY = 3


async def main(
    prompt_type: str,
    limit: Optional[int] = None,
):
    file = Path("prompts") / f"{prompt_type}.yaml"

    if not file.exists():
        raise FileNotFoundError(
            f"Prompt type '{prompt_type}' not found."
        )

    with file.open() as f:
        data = yaml.safe_load(f)

    prompts = data["prompts"]

    if limit is not None:
        prompts = prompts[:limit]

    handler = RequestHandler()

    semaphore = asyncio.Semaphore(CONCURRENCY)

    async def run(prompt, model_config):
        async with semaphore:
            return await handler.process_request(
                prompt=prompt["prompt"],
                model_config=model_config,
            )

    tasks = [
        asyncio.create_task(
            run(prompt, model_config)
        )
        for model_config in MODEL_REGISTRY.values()
        for prompt in prompts
    ]

    return await asyncio.gather(*tasks)


if __name__ == "__main__":
    results = asyncio.run(
        main(
            "simple",
            limit=1,
        )
    )

    for result in results:
        print(result)