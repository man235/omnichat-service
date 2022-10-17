from pkg_resources import require
from rest_framework import serializers
from sop_chat_service.app_connect.models import Attachment, Message
from sop_chat_service.zalo.utils.chat_support.type_constant import *


class ZaloTextMessage(serializers.Serializer):
    room_id = serializers.CharField(required=True)
    recipient_id = serializers.CharField(required=True)
    text = serializers.CharField(required=True)
    

class ZaloAttachmentMessage(serializers.Serializer):
    room_id = serializers.CharField(required=True)
    recipient_id = serializers.CharField(required=True)
    type = serializers.CharField(required=True) # file -attachment_token (doc, pdf, csv), image -attachment_id
    file = serializers.FileField(required=True)
    
    def check_file(self, request, data):
        attachment_type = data.get('type')
        file = request.FILES['file']
        
        try:
            file_extension = str(file.name).split('.')[1]
            file_type = '/'.join(file.content_type)
            # print(f'file_type1 -------- {file.type}')
            if attachment_type == FILE_MESSAGE:
                if file_extension in FILE_DOC_EXTENSION:
                    file_type = '/'.join([FILE_CONTENT_TYPE, FILE_MSWORD_EXTENSION])
                else:
                    file_type = '/'.join([FILE_CONTENT_TYPE, file_extension])
            elif attachment_type == IMAGE_MESSAGE:
                file_type = '/'.join([attachment_type, file_extension])
            else:
                raise serializers.ValidationError({
                    'message': f'Invalid type. No support for {attachment_type}'
                })
        except Exception as e:
            raise serializers.ValidationError({
                'message': 'Can not format file type'
            })
                    
        return file, file_type