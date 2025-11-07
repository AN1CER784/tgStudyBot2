import os
from celery import Celery
from datetime import timedelta

celery_app = Celery(
    "tg_bot",
    broker=os.getenv("CELERY_BROKER_URL", "redis://redis:6379/0"),
    include=["tasks"],
)

celery_app.conf.update(
    task_ignore_result=True,
    timezone="Europe/Moscow",
    enable_utc=False,
    beat_schedule={
        "dispatch-daily-messages": {
            "task": "tasks.dispatch_daily_messages",
            "schedule": timedelta(days=1),
        },
    },
)
