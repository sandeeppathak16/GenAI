import os
from dotenv import load_dotenv

load_dotenv()

from celery import Celery

celery_app = Celery(
    "llm_router",
    broker=os.getenv("REDIS_URL"),
    backend=os.getenv("REDIS_URL"),
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
)