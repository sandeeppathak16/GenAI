from time import perf_counter

from langchain_ollama import ChatOllama

from .model import ModelConfig, ModelProvider, ModelResponse
from logger import get_logger

logger = get_logger(__name__)


class RequestHandler:
    def __init__(self):
        self._llms: dict[str, ChatOllama] = {}

    async def process_request(
        self,
        prompt: str,
        model_config: ModelConfig,
    ) -> ModelResponse:
        logger.info(
            f"Processing request with LLM: '{model_config.display_name}' "
            f"(Runtime Model: '{model_config.runtime_model}', Provider: '{model_config.provider.value}')"
        )
        llm = self._get_llm(model_config)

        start = perf_counter()

        try:
            response = await llm.ainvoke(prompt)
        except Exception as e:
            logger.error(
                f"LLM invocation failed for model '{model_config.runtime_model}': {e}",
                exc_info=True,
            )
            raise

        latency = (perf_counter() - start) * 1000

        input_tokens, output_tokens, total_tokens = self.extract_usage(response)

        cost = self._calculate_cost(
            input_tokens,
            output_tokens,
            model_config,
        )

        logger.info(
            f"LLM invocation completed | Model: '{model_config.runtime_model}' | "
            f"Tokens (in/out/total): {input_tokens}/{output_tokens}/{total_tokens} | "
            f"Latency: {latency:.2f}ms | Cost: ${cost:.6f}"
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
            logger.info(f"Initializing new LLM instance for model '{model}'")
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
                logger.debug(f"Simulating OpenAI provider using Ollama model '{model_config.runtime_model}'")
                return ChatOllama(
                    model=model_config.runtime_model,
                    temperature=0,
                )

            case _:
                logger.error(f"Unsupported LLM provider requested: {model_config.provider}")
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