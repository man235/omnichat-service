from rest_framework import viewsets, permissions, serializers
from sop_chat_service.app_connect.serializers.reminder_serializers import ReminderSerializer, CreateReminderSerializer, UpdateReminderSerializer
from sop_chat_service.app_connect.models import Reminder, Room
from sop_chat_service.facebook.utils import custom_response

class ReminderViewSet(viewsets.ModelViewSet):
    queryset = Reminder.objects.all()
    permission_classes = (permissions.AllowAny, )
    serializer_class = ReminderSerializer

    def create(self, request, *args, **kwargs):
        data = request.data
        serializer = CreateReminderSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            room = Room.objects.get(room_id=data['room_id'])
            if not room:
                serializers.ValidationError({"room_id": "Room is not valid"})
            else:
                reminder=Reminder.objects.create(
                    room_id=room,
                    unit = data['unit'],
                    title = data['title'],
                    time_reminder = data['time_reminder'],
                    repeat_time = data['repeat_time']
                )
                sz = ReminderSerializer(reminder)
                return custom_response(200,"Create Reminder Successfully",sz.data)
    def update(self, request, pk=None, *args, **kwargs):
        data = request.data
        reminder = Reminder.objects.get(id=pk)
        serializer = ReminderSerializer(reminder,data=data,partial=True)
        serializer.is_valid(raise_exception=True)       
        serializer.save()
        return custom_response(200,"Update Reminder Successfully",serializer.data)
