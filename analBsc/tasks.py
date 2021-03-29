# Create your tasks here
from celery import shared_task
from .service import update_Db


@shared_task()
def update_database():
    print("updating")
    update_Db()
    print("endUpdating")



