import datetime
from pydantic import BaseModel, Field, create_model
from typing import Literal, Any, Optional



def build_output_model(schema: dict):

    fields = {}

    for name, info in schema.items():

        if info["type"] == "string":

            if "allowed_values" in info:
                typ = Literal[tuple(info["allowed_values"])]
            else:
                typ = str

        elif info["type"] == "integer":
            typ = int

        elif info["type"] == "float":
            typ = float

        elif info["type"] == "boolean":
            typ = bool

        else:
            typ = str

        fields[name] = (typ, Field(...))

    return create_model("OutputModel", **fields)


class PromptConfig(BaseModel):
    version: str
    system_prompt: str
    output_schema: dict[str, Any]
    few_shot_examples: list[dict] = []


class EvaluationResult(BaseModel):
    id: str
    input: str
    expected_category: str
    predicted_category: Optional[str]
    expected_summary: str
    predicted_summary: Optional[str]
    passed: bool
    latency_ms: float
    difficulty: str
    notes: str
    error: Optional[str] = None


class EvaluationRun(BaseModel):
    timestamp: datetime
    dataset_version: str
    prompt_version: str
    total: int
    passed: int
    failed: int
    accuracy: float
    average_latency_ms: float
    results: list[EvaluationResult]


class EvaluationDiff(BaseModel):
    previous_accuracy: float
    current_accuracy: float
    accuracy_delta: float
    previous_latency: float
    current_latency: float
    latency_delta: float
    regressions: list[EvaluationResult]
    improvements: list[EvaluationResult]
    regression_count: int
    improvement_count: int