import json
import uuid
from django.utils import timezone
from sop_chat_service.zalo.utils.api_suport.api_zalo_caller import get_message_data_of_zalo_user, send_zalo_message, upload_zalo_file
from rest_framework.response import Response
from rest_framework import serializers, viewsets, permissions
from rest_framework.decorators import action
from rest_framework import permissions, status
from sop_chat_service.app_connect.models import FanPage, Message, Room
from sop_chat_service.app_connect.api.page_serializers import FanPageSerializer
from sop_chat_service.facebook.utils import custom_response
from sop_chat_service.utils.request_headers import get_user_from_header
from sop_chat_service.zalo.serializers.zalo_chat_serializer import ZaloChatSerializer, ZaloUploadSerializer
import logging

from sop_chat_service.zalo.utils.chat_support.type_constant import TEXT_MESSAGE

logger = logging.getLogger(__name__)


class ZaloChatViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    permission_classes = (permissions.AllowAny, )
    serializer_class = ZaloChatSerializer
    
    @action(detail=False, methods=['post'], url_path='send')
    def send_message(self, request, *args, **kwargs) -> Response:
        user_header = get_user_from_header(request.headers)
        serializer = ZaloChatSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data_sz = serializer.data
        serializer.check_validation(validated_data_sz)
        
        queryset = Room.objects.filter(
            room_id = validated_data_sz.get('room_id'),
            user_id = user_header
        ).first()
    
        if queryset and queryset.page_id:
            if queryset.page_id.is_active:
                try:
                    oa_access_token = queryset.page_id.access_token_page
                    msg_type = validated_data_sz.get('message_type')
                    recipient_id = validated_data_sz.get('recipient_id')
                                   
                    rp_data = send_zalo_message(
                        msg_type = msg_type,
                        access_token = oa_access_token,
                        recipient_id = recipient_id,
                        text = validated_data_sz.get('text'),
                        attachment_id = validated_data_sz.get('attachment_id'),
                        attachment_token = validated_data_sz.get('attachment_token')
                    )
                
                    if not rp_data:
                        return custom_response(
                            403,
                            "Failed to call zalo open api to send message"
                        )
                    
                    if rp_data.get('message') == 'Failure':
                        return custom_response(
                            403,
                            'Failed to send message', 
                            rp_data.get('error')
                        )

                    return custom_response(
                        200, 
                        'Send message successfully',
                        rp_data.get('data')
                    )
                    
                except Exception as e:
                    return custom_response(500, json.dumps(str(e)))
            else:
                return custom_response(400, 'This Zalo OA is not active')
        else:
            return custom_response(400, 'This Room is not found')
        
    @action(detail=False, methods=['post'], url_path='upload')
    def upload(self, request, *args, **kwargs) -> Response:
        user_header = get_user_from_header(request.headers)
        serializer = ZaloUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        file_rq = serializer.check_validation(request, serializer.data)
        queryset = Room.objects.filter(
            room_id = serializer.data.get('room_id'),
            user_id = user_header,
        ).first()
        
        if not queryset or not queryset.page_id:
            return custom_response(400, 'Room or Zalo OA is not found')
        
        if queryset.page_id.is_active:              
            rp_data = upload_zalo_file (
                serializer.data.get('attachment_type'),
                access_token = queryset.page_id.access_token_page,
                file = file_rq
            )
                        
            if not rp_data:
                return custom_response(
                    400, 
                    'Can not call Zalo open api to upload'
                )
            else:
                if rp_data.get('message') == 'Failure':
                    return custom_response(
                        403,
                        'Call Zalo OA api successfully, but some error occured',
                        rp_data
                    )
                else:
                    return custom_response(
                        200,
                        'Upload successfully',
                        rp_data.get('data')
                    )
        else:
            return custom_response(400, "Zalo OA is not active")