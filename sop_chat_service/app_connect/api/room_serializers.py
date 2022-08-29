from rest_framework import serializers
from sop_chat_service.app_connect.models import Attachment, Message, Reminder, Room


class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = "__all__"


class RoomMessageSerializer(serializers.ModelSerializer):
    last_message = serializers.SerializerMethodField(source='get_last_message', read_only=True)

    class Meta:
        model = Room
        fields = ['id', 'last_message']

    def get_last_message(self, obj):
        last_message = Message.objects.filter(room_id=obj.id).order_by('-created_at').first()
        sz = LastMessageSerializer(last_message)
        return sz.data


class LastMessageSerializer(serializers.ModelSerializer):
    type_attachments = serializers.SerializerMethodField(source='get_type_attachments', read_only=True)

    class Meta:
        model = Message
        fields = ['id', 'text', 'type_attachments']

    def get_type_attachments(self, obj):
        attachment = Attachment.objects.filter(mid=obj.id).first()
        if attachment:
            return attachment.type
        else:
            return None


class ReminderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reminder
        fields = '__all__'
