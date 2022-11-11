from rest_framework import serializers
from sop_chat_service.app_connect.models import Room, Reminder,AssignReminder
from sop_chat_service.utils.request_headers import get_user_from_header
from django.db.models import Q


class CreateReminderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reminder
        fields = "__all__"


class ReminderSerializer(serializers.ModelSerializer):
    is_default = serializers.SerializerMethodField(source='get_is_default', read_only=True)
    class Meta:
        model = Reminder
        fields = ["id", "unit", "title", "time_reminder", "repeat_time",'is_default','created_at']

    def get_is_default(self , obj):
        if not obj.user_id:
            return True
        return False
class AssignReminderSerializer(serializers.Serializer):
    room_id = serializers.CharField(required=True)
    reminder_id = serializers.CharField(required=True)
    
    def validate(self,request,attrs):
        user_header = get_user_from_header(request.headers)
        room = Room.objects.filter(room_id=attrs.get("room_id"), user_id=user_header).first()
        if not room:
            raise serializers.ValidationError({"room": "Room Invalid"})
        assign =AssignReminder.objects.filter(room_id = room,user_id=user_header).order_by('-created_at').first()
        if assign:
            if assign.repeat_time != 0:
                raise serializers.ValidationError({"room": "Room Had Assign Reminder"})
            else: 
                assign.is_active_reminder= False
                assign.save()
        reminder= Reminder.objects.filter((Q(user_id=user_header) | Q(user_id=None)),id = attrs.get('reminder_id')).first()
        if not reminder:
            raise serializers.ValidationError({"reminder": "Reminder Invalid"})

        return room,reminder,user_header
class GetAssignReminderSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssignReminder
        fields = ["id", "unit", "title", "time_reminder", "repeat_time","is_active_reminder"]
        
        
class DeactiveAssignReminderSerializer(serializers.Serializer):
    assign_reminder_id = serializers.CharField(required=True)
    room_id = serializers.CharField(required=True)

    def validate(self,request,attrs):
        user_header = get_user_from_header(request.headers)
        room = Room.objects.filter(room_id=attrs.get("room_id"), user_id=user_header).first()
        if not room:
            raise serializers.ValidationError({"room": "Room Invalid"})
        assign= AssignReminder.objects.filter(id = attrs.get('assign_reminder_id'),user_id=user_header,room_id = room).first()
        if not assign:
            raise serializers.ValidationError({"assign": "Room don't have reminder Invalid"})

        return room,assign,user_header