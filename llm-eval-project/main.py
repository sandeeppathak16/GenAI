import os
import asyncio
from dotenv import load_dotenv
from report_generator import ReportGenerator


load_dotenv()


async def main():
    dataset_version = os.getenv("EVAL_DATASET_VERSION", "v1")
    prompt_version = os.getenv("EVAL_PROMPT_VERSION", "v1")
    provider = os.getenv("EVAL_PROVIDER", "groq")
    model_name = os.getenv("EVAL_MODEL", "openai/gpt-oss-120b")

    report = await ReportGenerator().generate(
        dataset_version=dataset_version,
        prompt_version=prompt_version,
        provider=provider,
        model_name=model_name,
    )

    run = report["run"]
    diff = report["diff"]

    print(f"accuracy {run.accuracy}")

    if diff:
        print(f"accuracy_delta {diff.accuracy_delta}")
        print(f"regression_count {diff.regression_count}")


asyncio.run(main())