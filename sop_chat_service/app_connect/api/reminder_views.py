from rest_framework import viewsets, permissions, status, serializers
from rest_framework.response import Response
from sop_chat_service.app_connect.serializers.reminder_serializers import ReminderSerializer, CreateReminderSerializer, UpdateReminderSerializer
from sop_chat_service.app_connect.models import Reminder, Room


class ReminderViewSet(viewsets.ModelViewSet):
    queryset = Reminder.objects.all()
    permission_classes = (permissions.AllowAny, )
    serializer_class = ReminderSerializer

    def create(self, request, *args, **kwargs):
        data = request.data
        serializer = CreateReminderSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            room = Room.objects.get(id=data['room_id'])
            if not room:
                serializers.ValidationError({"room_id": "Room is not valid"})
            else:
                Reminder.objects.create(
                    room_id=room,
                    unit = data['unit'],
                    title = data['title'],
                    time_reminder = data['time_reminder'],
                    repeat_time = data['repeat_time']
                )
                return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, pk=None, *args, **kwargs):
        data = request.data
        serializer = UpdateReminderSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            reminder = Reminder.objects.get(id=pk)
            reminder.unit = data['unit']
            reminder.title = data['title']
            reminder.time_reminder = data['time_reminder']
            reminder.repeat_time = data['repeat_time']
            reminder.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
