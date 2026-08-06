from pydantic import BaseModel, Field
from datetime import datetime
from typing import Any, Generic, TypeVar


class RunPipelineResponse(BaseModel):
    trace_id: str
    status: str
    document_type: str
    summary: str


class RunPipelineRequest(BaseModel):
    document: str = Field(..., min_length=1)


class Span(BaseModel):
    step_name: str
    input: Any
    output: Any
    prompt: str | None = None
    response: str | None = None
    confidence: int | None = None
    latency_ms: float | None = None


class Trace(BaseModel):
    trace_id: str
    started_at: datetime
    finished_at: datetime | None = None
    status: str
    document: str
    spans: list[Span]
    final_output: Any | None = None
    error: str | None = None
    root_cause: str | None = None


class Entity(BaseModel):
    type: str
    value: str
    confidence: int


class ExtractedEntities(BaseModel):
    entities: list[Entity] = Field(default_factory=list)


class ClassificationResult(BaseModel):
    document_type: str
    confidence: int
    reasoning: str


class SummaryResult(BaseModel):
    summary: str
    confidence: int


class Span(BaseModel):
    step_name: str
    started_at: datetime
    finished_at: datetime
    status: str
    input: Any | None = None
    output: Any | None = None
    prompt: str | None = None
    raw_response: str | None = None
    model: str | None = None
    input_tokens: int | None = None
    output_tokens: int | None = None
    total_tokens: int | None = None
    latency_ms: float | None = None
    confidence: int | None = None
    error: str | None = None



T = TypeVar("T", bound=BaseModel)


class StepResult(BaseModel, Generic[T]):
    output: T

    prompt: str
    raw_response: str

    model: str

    input_tokens: int
    output_tokens: int
    total_tokens: int

    latency_ms: float

    confidence: int | None = None