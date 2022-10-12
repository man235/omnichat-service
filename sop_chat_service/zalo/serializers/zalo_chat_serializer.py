from rest_framework import serializers
from sop_chat_service.app_connect.models import Attachment, Message
from sop_chat_service.zalo.utils.chat_support.type_constant import *


class ZaloChatSerializer(serializers.Serializer):
    room_id = serializers.CharField(required=True)
    recipient_id = serializers.CharField(required=True)
    message_type = serializers.CharField(required=True)
    text = serializers.CharField(required=False)
    attachment_token = serializers.CharField(required=False)
    attachment_id = serializers.CharField(required=False)
    
    def check_validation(self, data):
        message_type_check = str(data.get('message_type')).lower()
        if message_type_check == TEXT_MESSAGE:
            if not data.get('text'):
                raise serializers.ValidationError('Text is required')
        elif message_type_check == FILE_MESSAGE:
            if not data.get('attachment_token'):
                raise serializers.ValidationError('Attachment token is required')
        elif message_type_check in (STICKER_MESSAGE, IMAGE_MESSAGE, GIF_MESSAGE):
            if not data.get('attachment_id'):
                raise serializers.ValidationError('Attachment id is required')
        else:
            raise serializers.ValidationError(f'Invalid message type. No support for {message_type_check}')
    
    
class ZaloUploadSerializer(serializers.Serializer):
    attachment_type = serializers.CharField(required=True)
    file = serializers.FileField(required=True)
    room_id = serializers.CharField(required=True)
    
    def check_validation(self, request, data):
        # Get content type
        attachment_type_check = str(data.get('attachment_type')).lower()
        file = request.FILES['file']       
        
        file_content_type = str(file.content_type).lower().split('/')[0]           
        
        # file_content_type = files.content_type
        if attachment_type_check == FILE_MESSAGE:
            if not file_content_type == 'application':
                raise serializers.ValidationError({
                    'message': 'Only support for doc, pdf, csv'
                })
        elif attachment_type_check == IMAGE_MESSAGE:
            if not file_content_type == 'image':
                raise serializers.ValidationError({
                    'message': 'Only support for png, jpeg'
                })
        elif attachment_type_check == GIF_MESSAGE:
            if not file_content_type == 'image':
                raise serializers.ValidationError({
                    'message': 'Only support for gif'
                })
        else:
            raise serializers.ValidationError({
                'message': f'Invalid file. No support for {attachment_type_check}'
            })
        
        return file
        
