from rest_framework import serializers
from sop_chat_service.app_connect.models import Attachment, Message, Room
from sop_chat_service.app_connect.serializers.room_serializers import AttachmentSerializer


class MessageSerializer(serializers.ModelSerializer):
    message_reply = serializers.SerializerMethodField(source='get_message_reply',read_only=True)
    attachments = serializers.SerializerMethodField(source='get_attachments', read_only=True)
    count_message_unseen = serializers.SerializerMethodField(source='get_count_message_unseen', read_only=True)
    def get_count_message_unseen(self,obj):
        count = Message.objects.filter(room_id=obj.room_id, is_seen__isnull=True).count()
        return count        
    def get_message_reply(self,obj):
        if obj.reply_id:
            message  = Message.objects.filter(room_id = obj.room_id,id = obj.reply_id).first()
            if message:
                text = message.text
                if message.text:
                    pass
                else:
                    attachment = Attachment.objects.filter(mid = message).first()
                    text =attachment.url
                message_reply = {
                    "id":message.id,
                    "text": text
                }
                return message_reply
    def get_attachments(self, obj):
        attachments = Attachment.objects.filter(mid=obj.id)
        id =[]
        for attachment in attachments:
            id.append(attachment.id)    
        
        
        return id
    class Meta: 
        model= Message
        fields = ['attachments','id','sender_id','recipient_id','reaction','reply_id',
            'text','message_reply','sender_name','is_sender','created_at', 'is_seen',"uuid",'count_message_unseen']
        