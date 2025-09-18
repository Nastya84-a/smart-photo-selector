from celery import Celery
import os

# Создаем Celery приложение
celery_app = Celery(
    'app_simple',
    broker=os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379/0'),
    backend=os.environ.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')
)

# Импортируем задачи из app_simple
from app_simple import analyze_photos_task

# Регистрируем задачу
celery_app.task(analyze_photos_task)
