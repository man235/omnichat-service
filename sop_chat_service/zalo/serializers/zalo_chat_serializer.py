from pyexpat import model
from attr import field
from rest_framework import serializers
from sop_chat_service.app_connect.models import Attachment, Message


class ZaloChatSerializer(serializers.Serializer):
    oa_id = serializers.CharField(required=True)
    room_id = serializers.CharField(required=False)
    recipient_id = serializers.CharField(required=True)
    text = serializers.CharField(required=True)
    
    
class ZaloUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attachment
        fields = ["type", "file", ]
