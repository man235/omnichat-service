
from datetime import datetime, timedelta
import json
import time
import uuid
import ujson
from django.conf import settings
from sop_chat_service.facebook.utils import custom_response
from sop_chat_service.utils.request_headers import get_user_from_header

from ..utils import  connect_nats_client_publish_websocket, format_message_room, format_room
from ...app_connect.models import Attachment, Message, Room
from core.utils import format_message
from sop_chat_service.live_chat.models import LiveChat, LiveChatRegisterInfo
from sop_chat_service.live_chat.api.serializer import CompletedRoomSerializer, LiveChatSerializer, MessageLiveChatSend, UpdateAvatarLiveChatSerializer
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.utils import timezone
import asyncio
from sop_chat_service.utils.storages import upload_file_to_minio
from core.stream.redis_connection import redis_client
from core import constants


from iteration_utilities import unique_everseen

import logging
logger = logging.getLogger(__name__)



class LiveChatViewSet(viewsets.ModelViewSet):

    queryset = LiveChat.objects.all()
    serializer_class = LiveChatSerializer
    permission_classes = (permissions.AllowAny, )

    def list(self, request, *args, **kwargs):
        user_header = get_user_from_header(request.headers)
        qs = LiveChat.objects.filter(user_id = user_header).first()
        sz = LiveChatSerializer(qs, many=False)
        return custom_response(200,"Get Config Live Chat Successfully",sz.data)
    

    def create(self, request, *args, **kwargs):
        user_header = get_user_from_header(request.headers)
        
        # try:
        config = LiveChat.objects.filter(user_id = user_header).first()
        data = request.data
        if config:
            if data:
                data_config = data.get('live_chat', None)
                update_config = LiveChatSerializer(config, data=data_config, partial=True)
                update_config.is_valid(raise_exception=True)
                update_config.save()
                if data_config:
                    LiveChatRegisterInfo.objects.filter(live_chat_id=config).all().delete()
                    if data.get('registerinfo', None):
                        for item in data.get('registerinfo', None):
                            LiveChatRegisterInfo.objects.create(**item, live_chat_id=config)
                sz = LiveChatSerializer(config, many=False)
                redis_client.hset(constants.REDIS_CONFIG_LIVECHAT, sz.data['id'], str(ujson.dumps(sz.data)))
                message= 'Update success'
                return custom_response(200,message,sz.data['id'])
        else:
            if data:
                data_config = data.get('live_chat', None)
                if data_config:
                    live_chat = LiveChat.objects.create(**data_config,user_id = user_header)
                    if data.get('registerinfo', None):
                        for item in data.get('registerinfo', None):
                            LiveChatRegisterInfo.objects.create(**item, live_chat_id=live_chat)
                    sz = LiveChatSerializer(live_chat, many=False)
                    redis_client.hset(constants.REDIS_CONFIG_LIVECHAT, sz.data['id'], str(ujson.dumps(sz.data)))
                    message= 'Create success'
                    return custom_response(200,message,sz.data)
        # except Exception:
        #     return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def update(self, request, pk=None, *args, **kwargs):
        live_chat = self.get_object()
        data = request.data
        if request.data:
            if data['avatar']:
                update = UpdateAvatarLiveChatSerializer(live_chat,data=request.data)
                update.is_valid(raise_exception=True)
                update.save()
                message= 'Update success'
            qs = LiveChat.objects.filter(id =pk).first()
            sz = LiveChatSerializer(qs, many=False)
            redis_client.hset("live_chat-configs", sz.data['id'], str(sz.data))
            return custom_response(200,message,sz.data)
        return Response(200, status=status.HTTP_200_OK)

    @action(detail=False, methods=["GET"], url_path="room")
    def room(self, request, *args):
        user_header = get_user_from_header(request.headers)

        start_date=datetime.today() - timedelta(days=1)
        end_date=datetime.today()
        try:
            rooms = Room.objects.filter(user_id =user_header,type= 'live chat',
                                        room_message__is_sender = False).exclude(room_message__created_at__range = [start_date, end_date])
            if rooms:
                for room in unique_everseen(rooms):
                    Room.objects.filter(id = room.id).update(status="expired")
                return custom_response(200,"ok",[])
        except Exception:
            return custom_response(500,"INTERNAL_SERVER_ERROR",[])
    @action(detail=False, methods=["POST"], url_path="room/completed")
    def completed_room(self, request, *args):
        user_header = get_user_from_header(request.headers)
        data = request.data
        sz= CompletedRoomSerializer(data=data,many=False)
        sz.is_valid(raise_exception=True)
        room_id=sz.data['room_id']
        try:
            new_topic_publish = f'live-chat-room_{room_id}'
            room = Room.objects.filter(user_id =user_header,id = sz.data['room_id']).first()
            if room :
                room.status = "completed"
                room.completed_date = timezone.now()
                room.save()
                room_data = format_room(room)
                asyncio.run(connect_nats_client_publish_websocket(new_topic_publish, json.dumps(room_data).encode()))
                return custom_response(200,"ok",[])
        except Exception:
            return custom_response(500,"INTERNAL_SERVER_ERROR",[])

    @action(detail=False, methods=["POST"], url_path="send-message")
    def send_message(self, request, *args):
        user_header = get_user_from_header(request.headers)
        sz = MessageLiveChatSend(data=request.data, context={"request": request})
        sz.is_valid(raise_exception=True)
        # try:
        room_id = sz.data['room_id']
        room = Room.objects.filter(room_id = room_id, external_id=sz.data.get("recipient_id")).first()
        logger.debug(f"CHECK ROOM SEND MESSAGE LIVECHAT: {room} **************** ")
        # new_topic_publish = f'AnonymousLiveChat.Core.{room_id}'
        new_topic_publish = f'LiveChat.SaleMan.{room_id}'
        Message.objects.filter(room_id=room).update(is_seen= datetime.now())
        data_message={}
        if sz.data.get("mid"):
            message = Message.objects.get(id = sz.data.get("mid"))
            new_message = Message.objects.create(room_id=room,mid =message,recipient_id=room.external_id,is_sender=True,
                sender_id=user_header, text=sz.data.get('message_text'), uuid=uuid.uuid4(),created_at=datetime.now(),timestamp=int(time.time()))
            attachments = request.FILES.getlist('file')
            for attachment in attachments:
                new_attachment = Attachment.objects.create(
                    file=attachment, type=attachment.content_type, mid=new_message)
            logger.debug(f"SEND MESSAGE LIVECHAT WITH MID -> WS: {new_topic_publish} ****************  {new_message}")
            data_message = format_message(new_message) 
        else:
            new_message = Message.objects.create(room_id=room,is_sender=True, sender_id=user_header,
                recipient_id=room.external_id, text=sz.data.get('message_text'), uuid=uuid.uuid4(),created_at=datetime.now(),timestamp=int(time.time()))
            attachments = request.FILES.getlist('file')
            domain = settings.DOMAIN_MINIO_SAVE_ATTACHMENT
            sub_url = f"api/live_chat/chat_media/get_chat_media?name=live_chat_room_{room.room_id}/"
            for attachment in attachments:
                data_upload_file = upload_file_to_minio(attachment, room_id)
                logger.debug(f"ATTACHMENT {data_upload_file} +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ ")
                new_attachment = Attachment.objects.create(
                    file=data_upload_file, type=attachment.content_type,
                    mid=new_message, name=attachment.name,
                    url = str(domain+sub_url) + str(data_upload_file)
                )
            logger.debug(f"SEND MESSAGE LIVECHAT NOT WITH MID -> WS: {new_topic_publish} ****************  {new_message}")
            data_message = format_message(new_message)
        logger.debug(f"SEND MESSAGE LIVECHAT ******************************************************  {data_message}")
        asyncio.run(connect_nats_client_publish_websocket(f'live-chat-room.{room_id}', json.dumps(data_message).encode()))
        asyncio.run(connect_nats_client_publish_websocket(new_topic_publish, json.dumps(data_message).encode()))
        return custom_response(200,"ok",data_message)
        # except Exception:
        #     return custom_response(500,"INTERNAL_SERVER_ERROR",[])
