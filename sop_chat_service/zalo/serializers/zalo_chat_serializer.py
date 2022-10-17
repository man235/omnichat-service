from rest_framework import serializers
from sop_chat_service.zalo.utils.chat_support.type_constant import *  


class ZaloChatSerializer(serializers.Serializer):
    room_id = serializers.CharField(required=True)
    recipient_id = serializers.CharField(required=True)
    message_type = serializers.CharField(required=True)     # text, file, image
    text = serializers.CharField(required=False)
    attachment = serializers.FileField(required=False)
    
    def check_request_data(self, request, data):
        message_type_check = str(data.get('message_type')).lower()
        if message_type_check == TEXT_MESSAGE:
            if not data.get('text'):
                raise serializers.ValidationError({
                    'message': 'Text is required'
                })
                
            return True, None
        elif message_type_check in (FILE_MESSAGE, IMAGE_MESSAGE):
            attachment = request.FILES['attachment']
            if not attachment:                
                raise serializers.ValidationError({
                    'message': 'Attachment is required'
                })
                
            return False, attachment            
        else:
            raise serializers.ValidationError({
                'message': f'Invalid message type. No support for {message_type_check}'
            })
                    