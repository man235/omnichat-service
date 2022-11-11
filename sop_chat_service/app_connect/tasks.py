import time
import ujson
import asyncio
from core import constants
from celery import shared_task
from .models import AssignReminder
from core.utils import reminder_format_data, publish_data_to_nats, convert_unit_time


@shared_task(name = constants.CELERY_TASK_REMINDER_ROOM)
def create_reminder_task(id: int, repeat_time: int):
    try:
        _repeat = True
        while _repeat:
            assign = AssignReminder.objects.filter(id=id).first()
            if not assign:
                return "Error: Not Find Assign Reminder"
            if assign.repeat_time == 0:
                _repeat = False
            _time = convert_unit_time(assign.unit, assign.time_reminder)
            time.sleep(_time)
            assign.repeat_time = assign.repeat_time - 1 if assign.repeat_time == 1 else 0
            assign.is_active_reminder = True
            assign.save()
            reminder_ws = reminder_format_data(assign)
            subject_nats = f"{constants.REMINDER_CHAT_SERVICE_TO_WEBSOCKET}{assign.room_id}"
            asyncio.run(publish_data_to_nats(subject_nats, ujson.dumps(reminder_ws).encode()))
        return f"Reminder of room: {assign.room_id} with title {assign.title} success"
    except Exception as e:
        return f"Exception Create Task Reminder {e}"
