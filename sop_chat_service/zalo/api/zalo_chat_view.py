from django.utils import timezone
from rest_framework.response import Response
from rest_framework import serializers, viewsets, permissions
from rest_framework.decorators import action
from rest_framework import permissions, status
from config.settings.local import ZALO_APP_SECRET_KEY, ZALO_OA_OPEN_API
from sop_chat_service.app_connect.models import FanPage, Message
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
        queryset = FanPage.objects.filter(page_id=validated_data_sz.get("oa_id")).first()
        
        if queryset.is_active:
            try:
                zalo_msg_formatter = ZaloMessageDestination(
                    queryset.access_token_page,
                    recipient_id = validated_data_sz.get("recipient_id"),
                    message = {
                        'text': validated_data_sz.get("text"), 
                    }
                )
                
                response_data = MessageSendingContext(ZaloTextChatSender()).call_chat_sender(zalo_msg_formatter)
                
                if not response_data:
                    return custom_response(403, "Failed to call open api Zalo OA from Zalo")
                
                if response_data.get('message') == 'Success':
                    return custom_response(200, 'Success', response_data.get('data'))
                else:
                    return custom_response(200, response_data)
                
            except Exception as e:
                return custom_response(500, str(e))
        else:
            return custom_response(200, "This Zalo OA is not active")
        
    # @action(detail=False, methods=['post'], url_path='upload')
    # def upload(self, request, *args, **kwargs) -> Response:
    #     serializer = ZaloUploadSerializer(data=request.data)
        
    #     print(serializer)

    #     return custom_response(200, )