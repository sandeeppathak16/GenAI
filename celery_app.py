from celery import Celery
import os
from dotenv import load_dotenv
from celery.schedules import crontab

load_dotenv()

celery = Celery(
    "llm_router",
    broker=os.getenv("REDIS_URL"),
    backend=os.getenv("REDIS_URL"),
    include=[
        "multi_model_intelligent_routing_system.task",
    ],
)

celery.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
)

celery.conf.beat_schedule = {
    "retry-pending-evaluations": {
        "task": "retry_pending_evaluations",
        "schedule": crontab(minute="*/1"),
    },
    "daily-classifier-retraining": {
        "task": "retrain_classifier",
        "schedule": crontab(hour=2, minute=0)
    },
}