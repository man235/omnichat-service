from attr import field, fields_dict
from rest_framework import serializers
from sop_chat_service.app_connect.models import Message, Room
from sop_chat_service.zalo.utils.chat_support.type_constant import *  


class ZaloChatSerializer(serializers.Serializer):
    room_id = serializers.CharField(required=True)
    recipient_id = serializers.CharField(required=True)
    is_text = serializers.BooleanField(required=True)
    message_text = serializers.CharField(required=False)
    
    def check_validated_data(self, request, data):
        if data.get('is_text'):
            if not data.get('message_text'):
                raise serializers.ValidationError({
                    'message': 'Text is required'
                })
            return True, None
        else:
            attachments = request.FILES.getlist('file')
            if not attachments:
                raise serializers.ValidationError({
                    'message': 'Attachments is required'
                })
            return False, attachments

class ZaloQuotaSerializer(serializers.Serializer):
    room_id = serializers.CharField(required=True)
    is_active_quota = serializers.BooleanField(required=True)
    
    def check_validated_data(self, data):
        room_queryset = Room.objects.filter(room_id=data.get('room_id')).first()
        if not room_queryset:
            raise serializers.ValidationError({
                'message': 'Invalid Room'
            })

        return room_queryset
