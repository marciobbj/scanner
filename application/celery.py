from celery import Celery


app = Celery('Application')
app.config_from_object('application.celeryconfig')