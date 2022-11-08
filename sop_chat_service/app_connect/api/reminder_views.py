from sop_chat_service.app_connect.serializers.reminder_serializers import ReminderSerializer, CreateReminderSerializer, UpdateReminderSerializer
from sop_chat_service.app_connect.models import Reminder, Room
from rest_framework import viewsets, permissions, serializers
from .message_facebook_views import connect_nats_client_publish_websocket
from sop_chat_service.utils.request_headers import get_user_from_header
from sop_chat_service.app_connect.tasks import create_reminder_task
from sop_chat_service.facebook.utils import custom_response
from core.utils import format_log_message
from core import constants
import asyncio
import ujson


class ReminderViewSet(viewsets.ModelViewSet):
    queryset = Reminder.objects.all()
    permission_classes = (permissions.AllowAny, )
    serializer_class = ReminderSerializer

    def create(self, request, *args, **kwargs):
        user_header = get_user_from_header(request.headers)
        data = request.data
        serializer = CreateReminderSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            room = Room.objects.filter(room_id=data['room_id']).first()
            if not room:
                return custom_response(200,"Create Reminder Successfully",{"room_id": "Room is not valid"})
            else:
                reminder = Reminder.objects.create(
                    room_id=room,
                    unit = data['unit'],
                    title = data['title'],
                    time_reminder = data['time_reminder'],
                    repeat_time = data['repeat_time']
                )
                sz = ReminderSerializer(reminder)
                msg_log = f'You {constants.LOG_REMINDED} "{reminder.title}"'
                log_message = format_log_message(room, msg_log, constants.TRIGGER_REMINDED)
                subject_publish = f"{constants.CHAT_SERVICE_TO_CORECHAT_PUBLISH}.{room.room_id}"
                asyncio.run(connect_nats_client_publish_websocket(subject_publish, ujson.dumps(log_message).encode()))
                create_reminder_task.delay(reminder.id, reminder.repeat_time)
                return custom_response(200,"Create Reminder Successfully",sz.data)

    def update(self, request, pk=None, *args, **kwargs):
        user_header = get_user_from_header(request.headers)
        data = request.data
        reminder = Reminder.objects.filter(id=pk).first()
        room = Room.objects.filter(id=reminder.room_id.id).first()
        if not room:
            return custom_response(200,"Create Reminder Successfully",{"room_id": "Room is not valid"})
        serializer = CreateReminderSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        reminder.delete()
        new_reminder = Reminder.objects.create(
            room_id = room,
            unit = serializer.data.get('unit'),
            title = serializer.data.get('title'),
            time_reminder = serializer.data.get('time_reminder'),
            repeat_time = serializer.data.get('repeat_time')
        )
        # msg_log = f'{user_header} {constants.LOG_REMINDED} "{new_reminder.title}"'
        msg_log = f'You {constants.LOG_REMINDED} "{new_reminder.title}"'
        log_message = format_log_message(room, msg_log, constants.TRIGGER_REMINDED)
        subject_publish = f"{constants.CHAT_SERVICE_TO_CORECHAT_PUBLISH}.{room.room_id}"
        asyncio.run(connect_nats_client_publish_websocket(subject_publish, ujson.dumps(log_message).encode()))
        create_reminder_task.delay(new_reminder.id, new_reminder.repeat_time)
        return custom_response(200,"Update Reminder Successfully",serializer.data)
