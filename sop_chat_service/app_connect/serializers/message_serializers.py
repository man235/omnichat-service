from rest_framework import serializers
from sop_chat_service.app_connect.models import Attachment, Message, Room, ServiceSurvey, LogMessage
from sop_chat_service.app_connect.serializers.room_serializers import AttachmentSerializer, ServiceSurveySerializer, LogMessageSerializer
from sop_chat_service.utils.request_headers import get_user_from_header


class MessageSerializer(serializers.ModelSerializer):
    message_reply = serializers.SerializerMethodField(source='get_message_reply',read_only=True)
    attachments = serializers.SerializerMethodField(source='get_attachments', read_only=True)
    service_survey = serializers.SerializerMethodField(source='get_service_survey', read_only=True)
    log_message = serializers.SerializerMethodField(source='get_log_message', read_only=True)
    count_message_unseen = serializers.SerializerMethodField(source='get_count_message_unseen', read_only=True)

    def get_log_message(self,obj):
        _msg_log = LogMessage.objects.filter(mid = obj.id).first()
        sz = LogMessageSerializer(_msg_log)
        return sz.data
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
        sz = AttachmentSerializer(attachments, many=True)
        return sz.data
        # id =[]
        # for attachment in attachments:
        #     id.append(attachment.id)
        # return id
    def get_service_survey(self,obj):
        service_survey = ServiceSurvey.objects.filter(mid=obj.id)
        sz= ServiceSurveySerializer(service_survey,many=True)
        return sz.data
    class Meta: 
        model= Message
        fields = ['attachments','id','sender_id','recipient_id','reaction','reply_id',
            'text','message_reply','sender_name','is_sender','created_at', 'is_seen',"uuid",'count_message_unseen',"service_survey", "log_message"]
        
        
class ResultMessageSerializer(serializers.ModelSerializer):
    class Meta: 
        model= Message
        fields = ['id']
        
   
class LogMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model =LogMessage
        fields = ['mid','log_type','message','room_id','from_user','to_user']
class GetLogMessage(serializers.Serializer):
    customer_id = serializers.CharField(required=True)
    
    def validate(self,request,attrs):
        user_header = get_user_from_header(request.headers)
        room = Room.objects.filter(external_id=attrs.get("customer_id"), user_id=user_header).first()
        if not room:
            raise serializers.ValidationError({"room": "Room Invalid"})
        return room,user_header
    