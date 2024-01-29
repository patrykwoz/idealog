from celery import Celery, Task
from flask import Flask

def celery_init_app(app: Flask) -> Celery:
    class FlaskTask(Task):
        def __call__(self, *args: object, **kwargs: object) -> object:
            with app.app_context():
                return self.run(*args, **kwargs)

    celery_app = Celery(app.name, task_cls=FlaskTask)
    celery_app.config_from_object(app.config["CELERY"])
    celery_app.conf.result_expires = 3600
    celery_app.conf.worker_max_memory_per_child = 60000
    celery_app.conf.worker_prefetch_multiplier = 1
    celery_app.conf.worker_max_tasks_per_child = 1

    celery_app.set_default()
    app.extensions["celery"] = celery_app
    return celery_app