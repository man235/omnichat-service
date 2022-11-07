from celery import shared_task
from .models import Reminder
from core import constants
import time

@shared_task
def create_reminder_task(id: int, repeat_time: int):
    try:
        for repeat_time in range(0, repeat_time):
            reminder = Reminder.objects.filter(id=id).first()
            time_reminder = 1
            if reminder:
                return "Error"
            if reminder.unit == constants.DAY:
                time_reminder = reminder.time_reminder * 60 * 60 * 24
            elif reminder.unit == constants.HOUR:
                time_reminder = reminder.time_reminder * 60 * 60
            elif reminder.unit == constants.MINUTE:
                time_reminder = reminder.time_reminder * 60
            elif reminder.unit == constants.SECOND:
                time_reminder = reminder.time_reminder
            time.sleep(time_reminder)
            reminder.repeat_time = reminder.repeat_time - 1
            reminder.save()
        return "Success"
    except Exception as e:
        return f"Exception Create Task Reminder {e}"
