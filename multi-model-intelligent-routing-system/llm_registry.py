from model import ModelConfig, ModelProvider, QualityTier

from model import ModelConfig, ModelProvider, QualityTier

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