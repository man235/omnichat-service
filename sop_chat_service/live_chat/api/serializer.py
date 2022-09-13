
from rest_framework import serializers
from ...app_connect.models import Attachment, Message, Room
from sop_chat_service.live_chat.models import LiveChat, LiveChatRegisterInfo


class LiveChatSerializer(serializers.ModelSerializer):
    register_info = serializers.SerializerMethodField(source='get_register_info', read_only=True)

    class Meta:
        model = LiveChat
        fields = '__all__'

    def get_register_info(self, obj):
        register_info = LiveChatRegisterInfo.objects.filter(live_chat_id=obj.id)
        sz = RegisterInfoSerializer(data=register_info, many=True)
        sz.is_valid()
        return sz.data


class CreateLiveChatSerializer(serializers.ModelSerializer):
    class Meta:
        model = LiveChat
        fields = '__all__'


class RegisterInfoSerializer(serializers.ModelSerializer):

    class Meta:
        model = LiveChatRegisterInfo
        fields = '__all__'


class MessageLiveChatSerializer(serializers.ModelSerializer):
    attachments = serializers.FileField(required=False)
    sender_id = serializers.CharField(required=True)
    recipient_id = serializers.CharField(required=True)
    text = serializers.CharField(required=False)
    reply_id = serializers.CharField(required=False)
    is_sender = serializers.BooleanField(default=True)

    class Meta:
        model = Message
        fields = ['attachments', 'sender_id', 'recipient_id', 'text', 'reply_id', 'is_sender']


class AttachmentSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField(source='get_url', read_only=True)

    class Meta:
        model = Attachment
        fields = ['mid', 'type', 'url']

    def get_url(self, obj):
        return obj.file.url


class GetMessageLiveChatSerializer(serializers.ModelSerializer):
    attachments = serializers.SerializerMethodField(source='get_attachments', read_only=True)

    class Meta:
        model = Message
        fields = ['attachments', 'sender_id', 'recipient_id', 'text', 'reply_id', 'is_sender']

    def get_attachments(self, obj):
        attachments = Attachment.objects.filter(mid=obj.id)
        sz = AttachmentSerializer(attachments, many=True)
        return sz.data


class RoomSerializer(serializers.ModelSerializer):
    last_message = serializers.SerializerMethodField(source='get_last_message', read_only=True)

    class Meta:
        model = Room
        fields = ['id', 'name', 'approved_date', 'type', 'completed_date', 'last_message']

    def get_last_message(self, obj):
        message = Message.objects.filter(room_id=obj).order_by('-id').first()
        sz = GetMessageLiveChatSerializer(message)
        return sz.data
