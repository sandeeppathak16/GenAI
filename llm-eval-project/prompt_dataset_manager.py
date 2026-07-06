import yaml
from pathlib import Path
from models import PromptConfig


class PromptDatasetManager:

    def __init__(self, dir="prompts"):
        self.dir = Path(dir)

    def get(self, version: str) -> PromptConfig:
        file = self.dir / f"{version}.yaml"

        if not file.exists():
            raise FileNotFoundError(f"Prompt version '{version}' not found.")

        with open(file) as f:
            data = yaml.safe_load(f)

        return PromptConfig(
            version=data["version"],
            system_prompt=data["system_prompt"],
            output_schema=data["output_schema"],
            few_shot_examples=data.get("few_shot_examples", []),
        )