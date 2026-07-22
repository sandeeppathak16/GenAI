from dataclasses import dataclass
import re


@dataclass(frozen=True)
class PromptFeatures:
    word_count: int
    character_count: int

    has_json: bool
    has_code: bool
    has_table: bool

    has_extract: bool
    has_summarize: bool
    has_compare: bool
    has_translate: bool
    has_design: bool
    has_analyze: bool

    question_count: int
    line_count: int
    constraint_count: int


KEYWORDS = {
    "extract": "has_extract",
    "summarize": "has_summarize",
    "compare": "has_compare",
    "translate": "has_translate",
    "design": "has_design",
    "analyze": "has_analyze",
}


class FeatureExtractor:

    def extract(self, prompt: str) -> PromptFeatures:
        lower = prompt.lower()

        return PromptFeatures(
            word_count=len(prompt.split()),
            character_count=len(prompt),

            has_json="json" in lower,

            has_code="```" in prompt,

            has_table="table" in lower,

            has_extract="extract" in lower,

            has_summarize="summarize" in lower,

            has_compare="compare" in lower,

            has_translate="translate" in lower,

            has_design="design" in lower,

            has_analyze="analyze" in lower,

            question_count=prompt.count("?"),

            line_count=len(prompt.splitlines()),

            constraint_count=len(
                re.findall(
                    r"\b(must|should|return|only|exactly|include)\b",
                    lower,
                )
            ),
        )