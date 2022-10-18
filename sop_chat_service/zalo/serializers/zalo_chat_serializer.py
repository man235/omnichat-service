from rest_framework import serializers
from sop_chat_service.zalo.utils.chat_support.type_constant import *  


class ZaloChatSerializer(serializers.Serializer):
    room_id = serializers.CharField(required=True)
    recipient_id = serializers.CharField(required=True)
    is_text = serializers.BooleanField(required=True)
    text = serializers.CharField(required=False)
    attachment = serializers.FileField(required=False)
    
    def check_validated_data(self, request, data):
        if data.get('is_text'):
            if not data.get('text'):
                raise serializers.ValidationError({
                    'message': 'Text is required'
                })
            
            return True, None
        else:
            attachments = request.FILES.getlist('attachment')
            
            if not attachments:                
                raise serializers.ValidationError({
                    'message': 'Attachments is required'
                })
            
            return False, attachments
                    