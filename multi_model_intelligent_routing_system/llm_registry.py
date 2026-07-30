from .classifier.predict import PromptClassifier
from .model import ModelConfig, ModelProvider, QualityTier
from logger import get_logger

logger = get_logger(__name__)


MODEL_REGISTRY = {
    "gpt-4o-mini": ModelConfig(
        provider=ModelProvider.OPENAI,
        display_name="GPT-4o Mini (Simulated)",
        runtime_model="qwen3:4b",
        input_cost_per_million_tokens=0.15,
        output_cost_per_million_tokens=0.60,
        average_latency_ms=800,
        quality_tier=QualityTier.LOW,
    ),

    "llama3": ModelConfig(
        provider=ModelProvider.OLLAMA,
        display_name="Llama 3",
        runtime_model="llama3:latest",
        input_cost_per_million_tokens=0.50,
        output_cost_per_million_tokens=1.50,
        average_latency_ms=1200,
        quality_tier=QualityTier.MEDIUM,
    ),

    "gpt-4o": ModelConfig(
        provider=ModelProvider.OPENAI,
        display_name="GPT-4o (Simulated)",
        runtime_model="qwen3:8b",
        input_cost_per_million_tokens=2.50,
        output_cost_per_million_tokens=10.00,
        average_latency_ms=2200,
        quality_tier=QualityTier.HIGH,
    ),
}


def get_highest_quality_model() -> ModelConfig:
    return max(
        MODEL_REGISTRY.values(),
        key=lambda model: model.quality_tier.value,
    )


EVALUATION_MODEL = ModelConfig(
    provider=ModelProvider.OPENAI,
    display_name="GPT-4.1 Judge",
    runtime_model="qwen3:8b",
    input_cost_per_million_tokens=2.50,
    output_cost_per_million_tokens=10.00,
    average_latency_ms=2200,
    quality_tier=QualityTier.HIGH,
)


class Router:

    def __init__(self):
        self.classifier = PromptClassifier()

    def route(self, prompt: str):
        tier = self.classifier.predict(prompt)
        logger.info(f"Prompt classifier predicted tier: '{tier}'")

        match tier:
            case "simple":
                selected = MODEL_REGISTRY["gpt-4o-mini"]
            case "moderate":
                selected = MODEL_REGISTRY["llama3"]
            case "complex":
                selected = MODEL_REGISTRY["gpt-4o"]
            case _:
                logger.error(f"Classification returned unknown tier: '{tier}'")
                raise ValueError(f"Unknown tier: {tier}")

        logger.info(f"Router mapped tier '{tier}' -> Model '{selected.display_name}' ({selected.runtime_model})")
        return selected