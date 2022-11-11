from core.schema import ReminderSchema
from sop_chat_service.app_connect.models import AssignReminder
from core import constants


def reminder_format_data(assign_remind: AssignReminder):
    _reminder = ReminderSchema(
        room_id = assign_remind.room_id.room_id,
        user_id = assign_remind.user_id,
        unit = assign_remind.unit,
        title = assign_remind.title,
        time_reminder = int(assign_remind.time_reminder),
        repeat_time = int(assign_remind.repeat_time),
        created_at = str(assign_remind.created_at),
        is_active_reminder = True,
        event = constants.REMINDER_SALEMAN
    )
    return _reminder.dict()
