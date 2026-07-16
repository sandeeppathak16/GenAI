from time import perf_counter

from langchain_ollama import ChatOllama

from model import ModelConfig, ModelProvider, ModelResponse


class RequestHandler:
    def __init__(self):
        self._llms: dict[str, ChatOllama] = {}

    async def process_request(
        self,
        prompt: str,
        model_config: ModelConfig,
    ) -> ModelResponse:
        llm = self._get_llm(model_config)

        start = perf_counter()

        response = await llm.ainvoke(prompt)

        latency = (perf_counter() - start) * 1000

        input_tokens, output_tokens, total_tokens = self.extract_usage(response)

        cost = self._calculate_cost(
            input_tokens,
            output_tokens,
            model_config,
        )

        return ModelResponse(
            text=response.content,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=total_tokens,
            latency_ms=latency,
            cost=cost,
            provider=model_config.provider.value,
            model=model_config.display_name,
        )

    def _calculate_cost(
        self,
        input_tokens: int,
        output_tokens: int,
        config: ModelConfig,
    ) -> float:
        return (
            input_tokens * config.input_cost_per_million_tokens
            + output_tokens * config.output_cost_per_million_tokens
        ) / 1_000_000

    def _get_llm(self, model_config: ModelConfig):
        model = model_config.runtime_model

        if model not in self._llms:
            self._llms[model] = self._create_llm(model_config)

        return self._llms[model]

    def _create_llm(self, model_config: ModelConfig):
        match model_config.provider:
            case ModelProvider.OLLAMA:
                return ChatOllama(
                    model=model_config.runtime_model,
                    temperature=0,
                )

            case ModelProvider.OPENAI:
                # Simulated using Ollama for now
                return ChatOllama(
                    model=model_config.runtime_model,
                    temperature=0,
                )

            case _:
                raise ValueError(
                    f"Unsupported provider: {model_config.provider}"
                )
            
    @staticmethod
    def extract_usage(response):
        metadata = response.response_metadata or {}

        token_usage = metadata.get("token_usage")
        if token_usage:
            return (
                token_usage.get("prompt_tokens", 0),
                token_usage.get("completion_tokens", 0),
                token_usage.get("total_tokens", 0),
            )

        prompt_tokens = metadata.get("prompt_eval_count", 0)
        completion_tokens = metadata.get("eval_count", 0)

        return (
            prompt_tokens,
            completion_tokens,
            prompt_tokens + completion_tokens,
        )