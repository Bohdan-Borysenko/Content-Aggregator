from celery import Celery

celery_app = Celery(
    "worker",
    broker="redis://insight_flow_redis:6379/0",
    backend="redis://insight_flow_redis:6379/0",
    include=['celery_tasks.tasks'] 
)

celery_app.conf.beat_schedule = {
    "update-articles-every-10-minutes": {
        "task": "celery_tasks.tasks.update_all_sources",
        "schedule": 600.0,
    },
}