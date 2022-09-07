from ..models import Attachment, Label, Message, Reminder
from rest_framework import serializers
from sop_chat_service.app_connect.models import Attachment, Message, Reminder, Room


class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = "__all__"


class AttachmentSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField(source='get_url', read_only=True)

    class Meta:
        model = Attachment
        fields = ['mid', 'type', 'url']

    def get_url(self, obj):
        return obj.file.url

class GetMessageSerializer(serializers.ModelSerializer):
    attachments = serializers.SerializerMethodField(source='get_attachments', read_only=True)

    class Meta:
        model = Message
        fields = ['attachments', 'sender_id', 'recipient_id', 'text', 'reply_id', 'is_sender']

    def get_attachments(self, obj):
        attachments = Attachment.objects.filter(mid=obj.id)
        sz = AttachmentSerializer(attachments, many=True)
        return sz.data

class LastMessageSerializer(serializers.ModelSerializer):
    type_attachments = serializers.SerializerMethodField(source='get_type_attachments', read_only=True)

    class Meta:
        model = Message


class RoomMessageSerializer(serializers.ModelSerializer):
    last_message = serializers.SerializerMethodField(source='get_last_message', read_only=True)
    unseen_message_count = serializers.SerializerMethodField(source='get_unseen_message_count', read_only=True)

    class Meta:
        model = Room
        fields = ['id', 'user_id', 'name', 'type', 'note', 'approved_date',
                  'completed_date', 'conversation_id', 'created_at', 'last_message', 'unseen_message_count']

    def get_last_message(self, obj):
        message = Message.objects.filter(room_id=obj).order_by('-id').first()
        sz = GetMessageSerializer(message)
        return sz.data

    def get_unseen_message_count(self, obj):
        count = Message.objects.filter(room_id=obj, is_seen__isnull=False).count()
        return count
