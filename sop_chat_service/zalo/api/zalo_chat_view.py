import json
from django.utils import timezone
from rest_framework.response import Response
from rest_framework import serializers, viewsets, permissions
from rest_framework.decorators import action
from rest_framework import permissions, status
from config.settings.local import ZALO_APP_SECRET_KEY, ZALO_OA_OPEN_API
from sop_chat_service.app_connect.models import FanPage, Message, Room
from sop_chat_service.app_connect.api.page_serializers import FanPageSerializer
from sop_chat_service.facebook.utils import custom_response
from sop_chat_service.utils.request_headers import get_user_from_header
from sop_chat_service.zalo.serializers.zalo_chat_serializer import ZaloChatSerializer, ZaloUploadSerializer
from sop_chat_service.zalo.utils.chat_suport.send_message import MessageSender, MessageSendingContext, ZaloMessageDestination, ZaloTextChatSender
import logging

logger = logging.getLogger(__name__)


class ZaloChatViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    permission_classes = (permissions.AllowAny, )
    serializer_class = ZaloChatSerializer
    
    @action(detail=False, methods=['post'], url_path='send')
    def send_message(self, request, *args, **kwargs) -> Response:
        serializer = ZaloChatSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data_sz = serializer.data
        queryset = Room.objects.filter(
            room_id = validated_data_sz.get('room_id'),
        ).first()

        if queryset:
            if queryset.page_id:
                if queryset.page_id.is_active:
                    try:
                        oa_access_token = queryset.page_id.access_token_page
                        
                        zalo_msg_formatter = ZaloMessageDestination(
                            access_token = oa_access_token,
                            recipient_id = validated_data_sz.get("recipient_id"),
                            message = {
                                'text': validated_data_sz.get("text"), 
                            }
                        )
                        
                        response_data = MessageSendingContext(ZaloTextChatSender()).call_chat_sender(zalo_msg_formatter)
                        
                        if not response_data:
                            return custom_response(
                                403,
                                "Failed to call zalo open api to send message"
                            )
                        
                        if response_data.get('message') == 'Success':
                            return custom_response(
                                200, 'Send message successfully',
                                response_data.get('data')
                            )
                        else:
                            return custom_response(
                                200,
                                "Failed to send message", 
                                response_data
                            )
                        
                    except Exception as e:
                        return custom_response(500, json.dumps(str(e)))
                else:
                    return custom_response(400, "This Zalo OA is not active")
            else:
                return custom_response(403, "Can not find oa_id in room")
        else:
            return custom_response(400, "This Room is not found")
        
    # @action(detail=False, methods=['post'], url_path='upload')
    # def upload(self, request, *args, **kwargs) -> Response:
    #     serializer = ZaloUploadSerializer(data=request.data)
        
    #     print(serializer)

    #     return custom_response(200, )