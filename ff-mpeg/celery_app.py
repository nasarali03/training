from celery import Celery

celery_app = Celery(
    "stream_manager",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0"
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
)

# 👇 Add this line so Celery knows about your tasks
celery_app.autodiscover_tasks(['tasks'])
