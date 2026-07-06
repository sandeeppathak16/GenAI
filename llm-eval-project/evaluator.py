import asyncio
import time

from langchain_core.prompts import ChatPromptTemplate
from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint

from models import EvaluationResult, build_output_model
from prompt_dataset_manager import PromptDatasetManager


def chunk(elements, size=20):
    for i in range(0, len(elements), size):
        yield elements[i:i + size]


class Evaluator:

    def __init__(
        self,
        prompt_version: str,
        model_name: str = "Qwen/Qwen3-Coder-Next",
        batch_size: int = 20,
    ):
        self.prompt_version = prompt_version
        self.batch_size = batch_size
        self.model_name = model_name
        self.prompt_config = PromptDatasetManager().get(prompt_version)
        self.llm = self._build_llm()
        self.output_model = build_output_model(
            self.prompt_config.output_schema
        )
        self.prompt = self._build_prompt()
        self.chain = (
            self.prompt
            | self.llm.with_structured_output(self.output_model)
        )

    def _build_llm(self):
        huggingface = HuggingFaceEndpoint(
            repo_id=self.model_name,
        )

        return ChatHuggingFace(llm=huggingface)

    def _build_prompt(self):
        messages = [
            (
                "system",
                self.prompt_config.system_prompt,
            )
        ]

        for example in self.prompt_config.few_shot_examples:
            messages.append(
                (
                    "human",
                    example["input"],
                )
            )
            messages.append(
                (
                    "ai",
                    str(example["output"]),
                )
            )

        messages.append(
            (
                "human",
                "{email}",
            )
        )

        return ChatPromptTemplate.from_messages(messages)

    async def classify_email(self, message: str):
        return await self.chain.ainvoke(
            {
                "email": message,
            }
        )

    async def evaluate_case(self, test_case):
        start = time.perf_counter()

        try:

            prediction = await self.classify_email(
                test_case.input
            )

            latency = (
                time.perf_counter() - start
            ) * 1000

            return EvaluationResult(
                id=test_case.id,
                input=test_case.input,
                expected_category=test_case.expected.category,
                predicted_category=prediction.category,
                expected_summary=test_case.expected.summary,
                predicted_summary=prediction.summary,
                passed=(
                    prediction.category
                    == test_case.expected.category
                ),
                latency_ms=round(latency, 2),
                difficulty=test_case.expected_difficulty,
                notes=test_case.notes,
            )

        except Exception as e:
            latency = (
                time.perf_counter() - start
            ) * 1000

            return EvaluationResult(
                id=test_case.id,
                input=test_case.input,
                expected_category=test_case.expected.category,
                predicted_category=None,
                expected_summary=test_case.expected.summary,
                predicted_summary=None,
                passed=False,
                latency_ms=round(latency, 2),
                difficulty=test_case.expected_difficulty,
                notes=test_case.notes,
                error=str(e),
            )

    async def evaluate(
        self,
        dataset_version: str,
    ) -> list[EvaluationResult]:

        dataset = PromptDatasetManager("dataset").get(
            dataset_version
        )

        results = []

        total_batches = (
            len(dataset) + self.batch_size - 1
        ) // self.batch_size

        for batch_no, batch in enumerate(
            chunk(dataset, self.batch_size),
            start=1,
        ):

            print(
                f"Processing batch "
                f"{batch_no}/{total_batches}"
            )

            batch_results = await asyncio.gather(
                *[
                    self.evaluate_case(test_case)
                    for test_case in batch
                ]
            )

            results.extend(batch_results)

        return results