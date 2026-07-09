from dataclasses import dataclass
from enum import Enum


class ModelProvider(str, Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    OLLAMA = "ollama"


class QualityTier(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass(frozen=True)
class ModelConfig:
    provider: ModelProvider
    model_id: str

    input_cost_per_million_tokens: float
    output_cost_per_million_tokens: float

    average_latency_ms: int

    quality_tier: QualityTier