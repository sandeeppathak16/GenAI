import os
import json
import asyncio
import time

from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama
from langchain_groq import ChatGroq


from models import (
    EvaluationResult, build_output_model, 
    PromptConfig, DatasetItem
)
from yaml_manager import YamlManager


def chunk(elements, size=20):
    for i in range(0, len(elements), size):
        yield elements[i:i + size]


class Evaluator:

    def __init__(
        self,
        prompt_version: str,
        provider: str = "ollama",
        model_name: str = "llama3:latest",
        batch_size: int = 20,
    ):
        self.prompt_version = prompt_version
        self.batch_size = batch_size
        self.provider = provider.lower()
        self.model_name = model_name
        self.prompt_config = PromptConfig.model_validate(
            YamlManager("prompts").load(prompt_version)
        )
        self.llm = self._build_llm()
        self.output_model = build_output_model(
            self.prompt_config.output_schema
        )
        self.parser = JsonOutputParser(
            pydantic_object=self.output_model
        )
        self.prompt = self._build_prompt()
        self.chain = self.prompt | self.llm | self.parser

    def _build_llm(self):
        if self.provider == "ollama":
            return ChatOllama(
                model=self.model_name,
                temperature=0,
            )

        if self.provider == "groq":
            return ChatGroq(
                model=self.model_name,
                api_key=os.getenv("GROQ_API_KEY"),
                temperature=0,
            )

        raise ValueError(
            f"Unsupported provider: {self.provider}"
        )

    def _build_prompt(self):
        messages = [
            (
                "system",
                f"""
                {self.prompt_config.system_prompt}

                You must return a response matching the schema below.

                {{format_instructions}}
                """
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
                json.dumps(example["output"]).replace('{', '{{').replace('}', '}}')
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
        result = await self.chain.ainvoke(
            {
                "email": message,
                "format_instructions": (
                    self.parser.get_format_instructions()
                ),
            }
        )

        return self.output_model.model_validate(
            result
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

        dataset = YamlManager("dataset").load(
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
                    self.evaluate_case(
                        DatasetItem.model_validate(test_case)
                    )
                    for test_case in batch
                ]
            )

            results.extend(batch_results)

        return results