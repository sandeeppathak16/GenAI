from dataclasses import dataclass
from enum import Enum
from pydantic import BaseModel


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
    display_name: str
    runtime_model: str
    input_cost_per_million_tokens: float
    output_cost_per_million_tokens: float
    average_latency_ms: int
    quality_tier: QualityTier


@dataclass(frozen=True)
class ModelResponse:
    text: str
    input_tokens: int
    output_tokens: int
    total_tokens: int
    latency_ms: float
    cost: float
    provider: str
    model: str


class CompletionRequest(BaseModel):
    prompt: str