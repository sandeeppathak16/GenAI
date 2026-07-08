from datetime import datetime
from evaluator import Evaluator
from models import EvaluationRun
from report_storage import ReportStorage
from  slack_notifier import SlackNotifier



class ReportGenerator:

    def __init__(
        self,
        report_dir: str = "reports",
    ):
        self.storage = ReportStorage(report_dir)

    async def generate(
        self,
        dataset_version: str,
        prompt_version: str,
        provider: str,
        model_name: str
    ):
        evaluator = Evaluator(
            prompt_version=prompt_version,
            provider=provider,
            model_name=model_name,
        )

        results = await evaluator.evaluate(dataset_version)

        total = len(results)

        passed = sum(result.passed for result in results)

        failed = total - passed

        accuracy = (
            passed / total
            if total
            else 0
        )

        average_latency = (
            sum(
                r.latency_ms
                for r in results
            )
            / total
            if total
            else 0
        )

        run = EvaluationRun(
            timestamp=datetime.utcnow(),
            dataset_version=dataset_version,
            prompt_version=prompt_version,
            total=total,
            passed=passed,
            failed=failed,
            accuracy=round(
                accuracy,
                4,
            ),
            average_latency_ms=round(
                average_latency,
                2,
            ),
            results=results,
        )

        previous_run = self.storage.load_latest()

        diff = None

        if previous_run:
            diff = self.storage.compare(previous_run, run)

        self.storage.save(run)

        notifier = SlackNotifier()

        notifier.send(
            run=run,
            diff=diff,
        )

        return {
            "run": run,
            "diff": diff,
        }