import os
import requests
from typing import Optional

from models import EvaluationDiff, EvaluationRun


class SlackNotifier:

    def __init__(self):
        self.webhook_url = os.getenv(
            "SLACK_WEBHOOK_URL"
        )

    def send(
        self,
        run: EvaluationRun,
        diff: Optional[EvaluationDiff] = None,
    ):

        if not self.webhook_url:
            print("Slack webhook not configured.")
            return

        if diff is None:

            text = (
                "🟢 Initial Evaluation Run\n\n"
                f"Prompt: {run.prompt_version}\n"
                f"Accuracy: {run.accuracy:.2%}\n"
                f"Passed: {run.passed}/{run.total}"
            )

        else:

            status = "🟢 PASS"

            if diff.accuracy_delta < -0.08:
                status = "🔴 CRITICAL"

            elif diff.accuracy_delta < -0.03:
                status = "🟡 WARNING"

            text = (
                f"{status}\n\n"
                f"Prompt Version: {run.prompt_version}\n"
                f"Dataset Version: {run.dataset_version}\n\n"
                f"Accuracy: "
                f"{diff.previous_accuracy:.2%} → "
                f"{diff.current_accuracy:.2%}\n\n"
                f"Delta: {diff.accuracy_delta:.2%}\n"
                f"Regressions: {diff.regression_count}\n"
                f"Improvements: {diff.improvement_count}\n"
                f"Average Latency: {run.average_latency_ms:.2f} ms"
            )

        response = requests.post(
            self.webhook_url,
            json={
                "text": text,
            },
            timeout=30,
        )

        response.raise_for_status()