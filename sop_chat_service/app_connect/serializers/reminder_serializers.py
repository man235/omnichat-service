from rest_framework import serializers
from sop_chat_service.app_connect.models import Room, Reminder


class CreateReminderSerializer(serializers.ModelSerializer):
    room_id = serializers.IntegerField(required=True)
    unit = serializers.CharField(required=True)
    title = serializers.CharField(required=True)
    time_reminder = serializers.IntegerField(required=True)
    repeat_time = serializers.IntegerField(required=True)

    class Meta:
        model = Reminder
        fields = "__all__"

class UpdateReminderSerializer(serializers.Serializer):
    unit = serializers.CharField(required=True)
    title = serializers.CharField(required=True)
    time_reminder = serializers.IntegerField(required=True)
    repeat_time = serializers.IntegerField(required=True)

class ReminderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reminder
        fields = ["id", "unit", "title", "time_reminder", "repeat_time", "room_id"]
