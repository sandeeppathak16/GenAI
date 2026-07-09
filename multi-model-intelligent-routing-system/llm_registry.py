from model import ModelConfig, ModelProvider, QualityTier

MODEL_REGISTRY = {
    "gpt-4o": ModelConfig(
        provider=ModelProvider.OPENAI,
        model_id="qwen3:8b",
        input_cost_per_million_tokens=2.50,
        output_cost_per_million_tokens=10.00,
        average_latency_ms=1800,
        quality_tier=QualityTier.HIGH,
    ),
    "claude-sonnet": ModelConfig(
        provider=ModelProvider.ANTHROPIC,
        model_id="qwen3:8b",
        input_cost_per_million_tokens=3.00,
        output_cost_per_million_tokens=15.00,
        average_latency_ms=2200,
        quality_tier=QualityTier.HIGH,
    ),

    "claude-haiku": ModelConfig(
        provider=ModelProvider.ANTHROPIC,
        model_id="qwen3:8b",
        input_cost_per_million_tokens=0.80,
        output_cost_per_million_tokens=4.00,
        average_latency_ms=700,
        quality_tier=QualityTier.LOW,
    ),
    "llama3-local": ModelConfig(
        provider=ModelProvider.OLLAMA,
        model_id="llama3:latest",
        input_cost_per_million_tokens=0.05,
        output_cost_per_million_tokens=0.05,
        average_latency_ms=1200,
        quality_tier=QualityTier.MEDIUM,
    ),
}