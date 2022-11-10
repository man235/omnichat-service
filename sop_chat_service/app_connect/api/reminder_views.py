from sop_chat_service.app_connect.serializers.reminder_serializers import ReminderSerializer, CreateReminderSerializer
from sop_chat_service.app_connect.models import Reminder
from rest_framework import viewsets, permissions, serializers
from sop_chat_service.utils.request_headers import get_user_from_header
from sop_chat_service.facebook.utils import custom_response
from rest_framework.decorators import action
from django.db.models import Q

class ReminderViewSet(viewsets.ModelViewSet):
    queryset = Reminder.objects.all()
    permission_classes = (permissions.AllowAny, )
    serializer_class = ReminderSerializer




    @action(detail=False, methods=["POST"], url_path="list-reminder")
    def get_reminder(self, request, *args, **kwargs):
        user_header = get_user_from_header(request.headers)
        reminder = Reminder.objects.filter((Q(user_id=user_header) | Q(user_id=None))).order_by('-user_id','created_at')
        sz= ReminderSerializer(reminder,many=True)
        return custom_response(200,"Get List Reminder Successfully",sz.data)
    
    def create(self, request, *args, **kwargs):
        data = request.data
        user_header = get_user_from_header(request.headers)
        serializer = CreateReminderSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            reminder = Reminder.objects.create(
                user_id = user_header,
                unit = data['unit'],
                title = data['title'],
                time_reminder = data['time_reminder'],
                repeat_time = data['repeat_time']
            )
            sz = ReminderSerializer(reminder)
            return custom_response(200,"Create Reminder Successfully",sz.data)

    def update(self, request, pk=None, *args, **kwargs):
        user_header = get_user_from_header(request.headers)
        data = request.data
        reminder = Reminder.objects.filter(id=pk).first()
        if not reminder.user_id:
            return custom_response(400,"Can't Edit Default Reminder",[])
        serializer = CreateReminderSerializer(reminder,data=data,partial =True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return custom_response(200,"Update Reminder Successfully",serializer.data)
    def destroy(self, request, pk=None, *args, **kwargs):
        reminder = Reminder.objects.filter(id=pk).first()
        if not reminder.user_id:
            return custom_response(400,"Can't Delete Default Reminder",[])
        reminder.delete()
        return custom_response(200,"Delete Reminder Successfully",[])
