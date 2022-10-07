from pyexpat import model
from attr import field
from rest_framework import serializers
from sop_chat_service.app_connect.models import Attachment, Message


class ZaloChatSerializer(serializers.Serializer):
    room_id = serializers.CharField(required=True)
    recipient_id = serializers.CharField(required=True)
    text = serializers.CharField(required=True)
    message_type = serializers.CharField(required=True)
    
    
class ZaloUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attachment
        fields = ["type", "file", ]
