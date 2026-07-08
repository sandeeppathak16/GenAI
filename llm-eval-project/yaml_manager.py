import yaml
from pathlib import Path


class YamlManager:

    def __init__(self, directory: str):
        self.directory = Path(directory)

    def load(self, version: str):

        file = self.directory / f"{version}.yaml"

        if not file.exists():
            raise FileNotFoundError(
                f"Version '{version}' not found."
            )

        with open(file) as f:
            return yaml.safe_load(f)