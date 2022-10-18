from operator import is_
from django.utils import timezone
from sop_chat_service.zalo.utils.api_suport.api_zalo_caller import get_message_data_of_zalo_user, send_zalo_message, upload_zalo_attachment
from rest_framework.response import Response
from rest_framework import serializers, viewsets, permissions
from rest_framework.decorators import action
from core import constants
from rest_framework import permissions, status
from sop_chat_service.app_connect.models import Attachment, FanPage, Message, Room
from sop_chat_service.facebook.utils import custom_response
from sop_chat_service.utils.request_headers import get_user_from_header
from sop_chat_service.zalo.serializers.zalo_chat_serializer import ZaloChatSerializer
from sop_chat_service.zalo.utils.chat_support.format_message_zalo import format_attachment_type, format_sended_message_to_socket, reformat_attachment_type
from sop_chat_service.zalo.utils.chat_support.save_message_zalo import store_sending_message_database_zalo
from django.conf import settings
import nats
import asyncio
import json
import uuid
import logging

from sop_chat_service.zalo.utils.chat_support.type_constant import (
    FILE_CONTENT_TYPE,
    FILE_CSV_TYPE,
    FILE_DOC_EXTENSION,
    FILE_MESSAGE,
    FILE_MSWORD_EXTENSION,
    FILE_PDF_TYPE,
    IMAGE_MESSAGE,
    
)

logger = logging.getLogger(__name__)


async def connect_nats_client_publish_websocket(new_topic_publish, data_mid):
    nats_client = await nats.connect(settings.NATS_URL)
    await nats_client.publish(new_topic_publish, bytes(data_mid))
    await nats_client.close()
    return


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
        is_text_msg, validated_attachments = serializer.check_validated_data(
                                                request,
                                                validated_data_sz
                                            )
        queryset = Room.objects.filter(
            room_id=validated_data_sz.get('room_id'),
            user_id=user_header
        ).first()

        if not queryset or not queryset.page_id:
            return custom_response(400, 'Invalid Room')
    
        if not queryset.page_id.is_active:
            return custom_response(
                400,
                'Zalo OA is not active',
            )
            
        qs_oa_access_token = queryset.page_id.access_token_page
        qs_oa_id = queryset.page_id.page_id
        qs_room_id = queryset.room_id               
        validated_recipient_id = validated_data_sz.get('recipient_id')
        
        new_topic_publish = f'{constants.CHAT_SERVICE_TO_CORECHAT_PUBLISH}.{queryset.room_id}'
        
        if is_text_msg: # Send text message
            rp_send_data = send_zalo_message(
                access_token=qs_oa_access_token,
                recipient_id=validated_recipient_id,
                text=validated_data_sz.get('text'),
            )
            
            if not rp_send_data or rp_send_data.get('message') == 'Failure':
                return custom_response(
                    400,
                    'error',
                    'Failed to send message to Zalo'  
                )
            
            message_data_to_socket = format_sended_message_to_socket(
                text=validated_data_sz.get('text'),
                msg_id=rp_send_data.get('message_id'),
                oa_id=qs_oa_id,
                recipient_id=validated_recipient_id,
                room_room_id=qs_room_id,
                room_id=queryset.id,
                user_id=queryset.user_id                    
            )
            
            asyncio.run(connect_nats_client_publish_websocket(
                new_topic_publish,
                json.dumps(message_data_to_socket).encode())
            )
            
            return custom_response(
                200, 
                'Send message successfully',
                rp_send_data.get('data')
            )
        else:   # Send attachment messages
            successful_attachment_uploading = []     # keep the failed attachment when uploading
            successful_attachment_sending = []      # keep the failed attachment whenn sending
            
            for validated_attachment in validated_attachments:

                
                # Format attachment type of attachment from request
                # support for 'file', 'image'
                checked_attachment_type = format_attachment_type(validated_attachment) 

                # Upload attachment to zalo
                rp_upload_data = upload_zalo_attachment(
                    attachment_type=checked_attachment_type,
                    access_token=qs_oa_access_token,
                    attachment=validated_attachment
                )
                    
                if not rp_upload_data or rp_upload_data.get('message') == 'Failure':
                    
                    return custom_response(
                        400,
                        'Failed to upload attachment to Zalo',
                        {
                            'successful_uploading': successful_attachment_uploading,
                            'successful_sending': successful_attachment_sending
                        }
                    )
                else:
                    successful_attachment_uploading.append(validated_attachment.name)
                    
                    attachment_token = rp_upload_data.get('data').get('token', None)
                    attachment_id = rp_upload_data.get('data').get('attachment_id', None)

                    # Send attachment message to zalo
                    rp_send_data = send_zalo_message(
                        msg_type=checked_attachment_type,     # file, image
                        access_token=qs_oa_access_token,
                        recipient_id=validated_recipient_id,
                        attachment_token=attachment_token,
                        attachment_id=attachment_id
                    )
                    
                    if not rp_send_data or rp_send_data.get('message') == 'Failure':
                            return custom_response(
                                400,
                                'Failed to send attachment to Zalo'  ,
                                successful_attachment_sending
                            )
                    else:
                        successful_attachment_sending.append(validated_attachment.name)
                        rp_msg_id =rp_send_data.get('data').get('message_id')
                        
                        reformatted_attachment_type = reformat_attachment_type(validated_attachment)
                        
                        print(f'reformatted_attachment_type ------------- {reformatted_attachment_type}')
                        
                        # stored_attachment = store_sending_message_database_zalo(
                        #     room=queryset,
                        #     mid=rp_msg_id,
                        #     sender_id=queryset.page_id.page_id,
                        #     recipient_id=validated_recipient_id,
                        #     text=validated_data_sz.get('text'),
                        #     attachment=validated_attachment,
                        #     attachment_type=reformatted_attachment_type,
                        # )
                                            
                        # # Emit sended message to websocket
                        # if stored_attachment:                                        
                        #     socket_attachment = {
                        #         "id": str(stored_attachment.id),
                        #         "type": stored_attachment.type,
                        #         "name": stored_attachment.name,
                        #         "url": stored_attachment.url,
                        #         "size": str(stored_attachment.size),
                        #     }
                        # else:   # Failed to upload minio
                        socket_attachment = None                       
                                                
                        msg_socket_data_bundle = format_sended_message_to_socket(
                            attachments=[].append(validated_attachment)
                                if not socket_attachment 
                                else [].append(socket_attachment),     # get attachment from request instead of saved attachment
                            msg_id=rp_msg_id,
                            oa_id=qs_oa_id,
                            recipient_id=validated_recipient_id,
                            room_room_id=queryset.room_id,
                            room_id=queryset.id,
                            user_id=queryset.user_id
                        )
                                        
                        asyncio.run(connect_nats_client_publish_websocket(
                            new_topic_publish,
                            json.dumps(msg_socket_data_bundle).encode()
                        ))
                
            # Response successfully 
            # when all attachments were stored(database), uploaded(mino)
            return custom_response(
                200, 
                'Send message successfully',
                {
                    'successful_uploading': successful_attachment_uploading,
                    'successful_sending': successful_attachment_sending
                }
            )
                            