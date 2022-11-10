from celery import shared_task
from .models import AssignReminder
from core import constants
import time
from core.utils import format_log_message

@shared_task
def create_reminder_task(id: int, repeat_time: int):
    
    try:
        for repeat_time in range(0, repeat_time):
            assign = AssignReminder.objects.filter(id=id).first()
            time_reminder = 1
            if not assign:
                return "Error"
            if assign.unit == constants.DAY:
                time_reminder = assign.time_reminder * 60 * 60 * 24
            elif assign.unit == constants.HOUR:
                time_reminder = assign.time_reminder * 60 * 60
            elif assign.unit == constants.MINUTE:
                time_reminder = assign.time_reminder * 60
            elif assign.unit == constants.SECOND:
                time_reminder = assign.time_reminder
            time.sleep(time_reminder)
            assign.repeat_time = assign.repeat_time - 1
            assign.is_active_reminder = True 
            assign.save()
        return "Success"
    except Exception as e:
        return f"Exception Create Task Reminder {e}"
