from django.utils import timezone
from sop_chat_service.zalo.utils.api_suport.api_zalo_caller import get_message_data_of_zalo_user, send_zalo_message, upload_zalo_file
from rest_framework.response import Response
from rest_framework import serializers, viewsets, permissions
from rest_framework.decorators import action
from core import constants
from rest_framework import permissions, status
from sop_chat_service.app_connect.models import Attachment, FanPage, Message, Room
from sop_chat_service.facebook.utils import custom_response
from sop_chat_service.utils.request_headers import get_user_from_header
from sop_chat_service.zalo.serializers.zalo_chat_serializer import ZaloAttachmentMessage, ZaloTextMessage
from sop_chat_service.zalo.utils.chat_support.save_message_zalo import save_message_store_database_zalo, store_sending_message_database_zalo
import nats
import asyncio
from django.conf import settings
import json
import uuid
import logging

logger = logging.getLogger(__name__)


async def connect_nats_client_publish_websocket(new_topic_publish, data_mid):
    nats_client = await nats.connect(settings.NATS_URL)
    await nats_client.publish(new_topic_publish, bytes(data_mid))
    await nats_client.close()
    return


class ZaloChatViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    permission_classes = (permissions.AllowAny, )
    serializer_class = ZaloAttachmentMessage
        
    @action(detail=False, methods=['post'], url_path='send')
    def send_text_message(self, request, *args, **kwargs) -> Response:
        user_header = get_user_from_header(request.headers)
        
        serializer = ZaloTextMessage(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data_sz = serializer.data
            
        queryset = Room.objects.filter(
            room_id = validated_data_sz.get('room_id'),
            user_id = user_header
        ).first()

        if not queryset or not queryset.page_id:
            return custom_response(400, 'Invalid room or Zalo OA')
    
        if queryset.page_id.is_active:
            try:
                oa_access_token = queryset.page_id.access_token_page
                recipient_id = validated_data_sz.get('recipient_id')
                text = validated_data_sz.get('text')
                
                # Send file
                rp_send_data = send_zalo_message(
                    access_token = oa_access_token,
                    recipient_id = recipient_id,
                    text = validated_data_sz.get('text'),
                )
                
                
                if not rp_send_data:
                    return custom_response(
                        403,
                        "Failed to call zalo open api to send message"
                    )
                
                if rp_send_data.get('message') == 'Failure':
                    return custom_response(
                        403,
                        'Failed to send message', 
                        rp_send_data
                    )
                else:
                    msg_id = rp_send_data.get('data').get('message_id')
                    
                    store_sending_message_database_zalo(
                        room=queryset,
                        mid=msg_id,
                        sender_id=queryset.page_id.page_id,
                        recipient_id=recipient_id,
                        text = rp_send_data.get('text'),
                    )
                    
                    # Emit sended message to websocket
                    # msg_data_bundle = {
                    #     "mid": rp_send_data.get('data').get('message_id'),
                    #     "attachments": None,
                    #     "text": text,
                    #     "created_time": None,
                    #     "sender_id": queryset.page_id,
                    #     "recipient_id": rp_send_data.get('data').get('user_id'),
                    #     "room_id": queryset.room_id,
                    #     "is_sender": True,
                    #     "created_at": str(timezone.now()),
                    #     "is_seen": None,
                    #     "message_reply": None,
                    #     "reaction": None,
                    #     "reply_id": None,
                    #     "sender_name": None,
                    #     "uuid": str(uuid.uuid4()),
                    #     "msg_status": constants.SEND_MESSAGE_STATUS
                    # }
                    
                    # new_topic_publish = f'{constants.CHAT_SERVICE_TO_CORECHAT_PUBLISH}.{queryset.room_id}'
                    # asyncio.run(connect_nats_client_publish_websocket(
                    #     new_topic_publish,
                    #     json.dumps(msg_data_bundle).encode()
                    # ))
                    
                    return custom_response(
                        200, 
                        'Send message successfully',
                        rp_send_data.get('data')
                    )
            except Exception as e:
                return custom_response(403, json.dumps(str(e)))
        else:
            return custom_response(400, 'Zalo OA is not active')
        
        
    @action(detail=False, methods=['post'], url_path='send/attachment')
    def send_attachment_message(self, request, *args, **kwargs) -> Response:
        user_header = get_user_from_header(request.headers)
        
        serializer = ZaloAttachmentMessage(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data_sz = serializer.data
        file, file_type = serializer.check_file(request, validated_data_sz)
            
        queryset = Room.objects.filter(
            room_id = validated_data_sz.get('room_id'),
            user_id = user_header
        ).first()

        if not queryset or not queryset.page_id:
            return custom_response(400, 'Invalid room or Zalo OA')

        if queryset.page_id.is_active:
            try:
                oa_access_token = queryset.page_id.access_token_page
                recipient_id = validated_data_sz.get('recipient_id')
                
                # Upload file
                rp_upload_data = upload_zalo_file (
                    validated_data_sz.get('type'),
                    access_token = oa_access_token,
                    file = file
                )
                            
                if not rp_upload_data:
                    return custom_response(
                        403, 
                        'Can not upload'
                    )
                else:
                    if rp_upload_data.get('message') == 'Failure':
                        return custom_response(
                            403,
                            rp_upload_data,
                        )

                attachment_token = rp_upload_data.get('data').get('token')
                attachment_id = rp_upload_data.get('data').get('attachment_id')
                
                # Send file
                rp_send_data = send_zalo_message(
                    msg_type = validated_data_sz.get('type'),
                    access_token = oa_access_token,
                    recipient_id = recipient_id,
                    attachment_token = attachment_token,
                    attachment_id = attachment_id
                )
                
                if not rp_send_data:
                    return custom_response(
                        403,
                        "Failed to call zalo open api to send message"
                    )
                
                if rp_send_data.get('message') == 'Failure':
                    return custom_response(
                        403,
                        'Failed to send message', 
                        rp_send_data
                    )
                else:
                    msg_id =rp_send_data.get('data').get('message_id')
                    
                    saved_attachment = store_sending_message_database_zalo(
                        room = queryset,
                        mid = msg_id,
                        sender_id = queryset.page_id.page_id,
                        recipient_id = recipient_id,
                        attachment = file,
                        attachment_type = file_type,
                    )

                    logger.debug(f" SAVE SENDED MESSAGE +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ ")

                    # Emit sended message to websocket                                        
                    attachment = {
                        "id": str(saved_attachment.id),
                        "type": saved_attachment.type,
                        "name": saved_attachment.name,
                        "url": saved_attachment.url,
                        "size": str(saved_attachment.size),
                    }
                                        
                    msg_data_bundle = {
                        "mid": rp_send_data.get('data').get('message_id'),
                        "attachments": [attachment],
                        "text": None,
                        "created_time": str(timezone.now()),
                        "sender_id": queryset.page_id,
                        "recipient_id": rp_send_data.get('data').get('user_id'),
                        "room_id": queryset.room_id,
                        "is_sender": True,
                        "created_at": str(timezone.now()),
                        "is_seen": None,
                        "message_reply": None,
                        "reaction": None,
                        "reply_id": None,
                        "sender_name": None,
                        "uuid": str(uuid.uuid4()),
                        "msg_status": constants.SEND_MESSAGE_STATUS
                    }
                    
                    new_topic_publish = f'{constants.CHAT_SERVICE_TO_CORECHAT_PUBLISH}.{queryset.room_id}'
                    asyncio.run(connect_nats_client_publish_websocket(
                        new_topic_publish,
                        json.dumps(msg_data_bundle).encode()
                    ))
                    
                    return custom_response(
                        200, 
                        'Send message successfully',
                        rp_send_data.get('data')
                    )
            except Exception as e:
                return custom_response(403, json.dumps(str(e)))
        else:
            return custom_response(400, 'Zalo OA is not active')
    