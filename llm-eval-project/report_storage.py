import json
from pathlib import Path

from models import EvaluationRun, EvaluationDiff


class ReportStorage:

    def __init__(
        self,
        report_dir: str = "reports",
    ):
        self.report_dir = Path(report_dir)
        self.history_dir = self.report_dir / "history"
        self.latest_file = self.report_dir / "latest.json"

        self.report_dir.mkdir(exist_ok=True)

        self.history_dir.mkdir(exist_ok=True)

    def save(
        self,
        run: EvaluationRun,
    ):

        data = run.model_dump(mode="json")

        with open(self.latest_file, "w") as f:
            json.dump(data, f, indent=2)

        filename = (
            f"{run.timestamp:%Y%m%d_%H%M%S}"
            f"_{run.prompt_version}.json"
        )

        with open(self.history_dir/ filename, "w") as f:
            json.dump(data, f, indent=2)

    def load_latest(
        self,
    ) -> EvaluationRun | None:

        if not self.latest_file.exists():
            return None

        with open(self.latest_file) as f:
            data = json.load(f)

        return EvaluationRun.model_validate(
            data
        )

    def compare(
        self,
        previous: EvaluationRun,
        current: EvaluationRun,
    ) -> EvaluationDiff:
        previous_map = {
            result.id: result
            for result in previous.results
        }

        regressions = []
        improvements = []

        for result in current.results:
            old = previous_map.get(
                result.id
            )

            if old is None:
                continue

            if (
                old.passed
                and not result.passed
            ):
                regressions.append(
                    result
                )

            elif (
                not old.passed
                and result.passed
            ):
                improvements.append(
                    result
                )

        return EvaluationDiff(
            previous_accuracy=previous.accuracy,
            current_accuracy=current.accuracy,
            accuracy_delta=round(
                current.accuracy - previous.accuracy, 
                4
            ),
            regressions=regressions,
            improvements=improvements,
            regression_count=len(regressions),
            improvement_count=len(improvements),
        )