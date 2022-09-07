from rest_framework import serializers
from sop_chat_service.app_connect.models import Attachment, Message

class AttachmentSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField(source='get_url', read_only=True)
    class Meta:
        model = Attachment
        fields = ['mid', 'type', 'url','attachment_id']

    def get_url(self, obj):
        return obj.file.url

class MessageSerializer(serializers.ModelSerializer):
    message_reply = serializers.SerializerMethodField(source='get_message_reply',read_only=True)
    attachments = serializers.SerializerMethodField(source='get_attachments', read_only=True)
    
    def get_message_reply(self,obj):
        message  = Message.objects.get(room_id = obj)
        if message:
            text = message.text
            if message.text:
                pass
            else:
                attachment = Attachment.objects.get(mid=message)
                message_reply = {
                    "id":message.id,
                    "text": attachment.url
                }
            return message_reply
    def get_attachments(self, obj):
        attachments = Attachment.objects.filter(mid=obj.id)
        sz = AttachmentSerializer(attachments, many=True)
        return sz.data
    class Meta: 
        model= Message
        fields = ['attachments','id','sender_id','recipient_id','reaction','reply_id','text','sender_name','is_sender','created_at']