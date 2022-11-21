
from datetime import datetime, timedelta
import json
import time
import ujson
from django.conf import settings
from sop_chat_service.facebook.utils import custom_response
from sop_chat_service.utils.request_headers import get_email_from_header, get_user_from_header
import uuid

from ..utils import   saleman_send_message_to_anonymous
from ...app_connect.models import Attachment, Message, Room
from core.utils import format_message, format_message_to_nats_chat_message
from sop_chat_service.live_chat.models import LiveChat, LiveChatRegisterInfo
from sop_chat_service.live_chat.api.serializer import  CreateLiveChatSerializer, LiveChatSerializer, MessageLiveChatSend, RegisterInfoSerializer, UpdateAvatarLiveChatSerializer
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
import requests

logger = logging.getLogger(__name__)


class LiveChatViewSet(viewsets.ModelViewSet):

    queryset = LiveChat.objects.all()
    serializer_class = LiveChatSerializer
    permission_classes = (permissions.AllowAny, )

    def list(self, request, *args, **kwargs):
        user_header = get_user_from_header(request.headers)
        qs = LiveChat.objects.filter(user_id = user_header).first()
        sz = LiveChatSerializer(qs, many=False) 
        return custom_response(200,"Get Config Live Chat Successfully",sz.data if qs else None)
    

    def create(self, request, *args, **kwargs):
        user_header = get_user_from_header(request.headers)
        user_email=get_email_from_header(request.headers)
        query = {'email': user_email}
        user_profile = requests.get(f'{settings.GET_USER_PROFILE_URL}/api/user/profile', params=query)
        if user_profile.status_code == 200 and user_profile.json()['status'] == "success":
            data_user = user_profile.json()['data']
            config = LiveChat.objects.filter(user_id = user_header).first()
            data = request.data
            if config:
                if data:
                    data_config = data.get('live_chat', None)
                    update_config = CreateLiveChatSerializer(config, data=data_config, partial=True)
                    msg= update_config.validate(data_config)
                    info_sz = RegisterInfoSerializer(data= data.get('registerinfo'))
                    info = info_sz.validate(data.get('registerinfo'))
                    if msg :
                        return custom_response(400 ,msg,"Errors")
                    if info:
                        return custom_response(400 ,info,"Errors")
                    update_sz= LiveChatSerializer(config, data=data_config, partial=True)
                    update_sz.is_valid(raise_exception=True)
                    update_sz.save()
                    LiveChatRegisterInfo.objects.filter(live_chat_id=config).all().delete()

                    if data.get('registerinfo', None):
                        for item in data.get('registerinfo', None):
                            LiveChatRegisterInfo.objects.create(**item, live_chat_id=config)
                                
                    sz = LiveChatSerializer(config, many=False)
                    data = {
                        "user_info" : {
                            "name":data_user['name'],
                            "avatar":""
                            },
                        "config" : sz.data, 
                    }
                    redis_client.hset(constants.REDIS_CONFIG_LIVECHAT, sz.data['id'], str(ujson.dumps(data)))
                    message= 'Update success'
                    return custom_response(200,message,sz.data['id'])
            else:
                if data:
                    data_config = data.get('live_chat', None)
                    if data_config:
                        live_chat = CreateLiveChatSerializer(data=data_config)
                        msg= live_chat.validate(data.get('live_chat', None))
                        info_sz = RegisterInfoSerializer(data= data.get('registerinfo',None))
                        info = info_sz.validate(data.get('registerinfo'))
                        if msg:
                            return custom_response(400 ,msg,"Errors")
                        if info:
                            return custom_response(400 ,msg,"Errors")
                        live_chat = LiveChat.objects.create(**data_config,user_id = user_header)
                        if data.get('registerinfo', None):
                            for item in data.get('registerinfo', None):
                                LiveChatRegisterInfo.objects.create(**item, live_chat_id=live_chat)
                        sz = LiveChatSerializer(live_chat, many=False)
                        data = {
                        "user_info" : {
                            "name":"SaleMan",
                            "avatar":""
                            },
                        "config" : sz.data,
                        }
                        redis_client.hset(constants.REDIS_CONFIG_LIVECHAT, sz.data['id'], str(ujson.dumps(data)))
                        message= 'Create success'
                        return custom_response(200,message,sz.data)
        else:
            return custom_response(500,"HTTP_500_INTERNAL_SERVER_ERROR",[])
                       


    def update(self, request, pk=None, *args, **kwargs):
        user_email=get_email_from_header(request.headers)
        query = {'email': user_email}
        user_profile = requests.get(f'{settings.GET_USER_PROFILE_URL}/api/user/profile', params=query)
        if  user_profile.status_code == 200 and user_profile.json()['status'] == "success":
            data_user = user_profile.json()['data']
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
                data = {
                        "user_info" : {
                            "name":data_user['name'],
                            "avatar":""
                            },
                        "config" : sz.data, 
                    }
                redis_client.hset(constants.REDIS_CONFIG_LIVECHAT, sz.data['id'], str(ujson.dumps(data)))
                return custom_response(200,message,sz.data)
            return Response(200, status=status.HTTP_200_OK)
        else:
            return custom_response(500,"HTTP_500_INTERNAL_SERVER_ERROR",[])

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

    @action(detail=False, methods=["POST"], url_path="send-message")
    def send_message(self, request, *args):
        user_header = get_user_from_header(request.headers)
        sz = MessageLiveChatSend(data=request.data, context={"request": request})
        sz.is_valid(raise_exception=True)
        room_id = sz.data['room_id']
        room = Room.objects.filter(room_id = room_id).first()
        data_message={}
        if sz.data.get("mid"):
            message = Message.objects.get(id = sz.data.get("mid"))
            new_message = Message.objects.create(room_id=room,mid =message,recipient_id=room.external_id,is_sender=True,
                sender_id=user_header, text=sz.data.get('message_text'), uuid=uuid.uuid4(),created_at=datetime.now(),timestamp=int(time.time()))
            attachments = request.FILES.getlist('file')
            for attachment in attachments:
                new_attachment = Attachment.objects.create(
                    file=attachment, type=attachment.content_type, mid=new_message)
            data_message = format_message(new_message)
        else:
            new_message = Message.objects.create(room_id=room,is_sender=True, sender_id=user_header,
                recipient_id=room.external_id, text=sz.data.get('message_text'), uuid=uuid.uuid4(),created_at=datetime.now(),timestamp=int(time.time()))
            attachments = request.FILES.getlist('file')
            domain = settings.DOMAIN_MINIO_SAVE_ATTACHMENT
            sub_url = f"api/live_chat/chat_media/get_chat_media?name={constants.LIVECHAT_ROOM_MINIO}_{room.room_id}/"
            for attachment in attachments:
                data_upload_file = upload_file_to_minio(attachment, room_id, constants.LIVECHAT_ROOM_MINIO)
                Attachment.objects.create(
                    file=data_upload_file, type=attachment.content_type,
                    mid=new_message, name=attachment.name,
                    size= attachment.size,
                    url = str(domain+sub_url) + str(data_upload_file)
                )
            data_message = format_message_to_nats_chat_message(room, new_message)
        Message.objects.filter(room_id=room).update(is_seen= datetime.now())
        asyncio.run(saleman_send_message_to_anonymous(room, data_message))
        logger.debug(f"SEND MESSAGE LIVECHAT ******************************************************  {data_message}")
        return custom_response(200,"ok",data_message)

    @action(detail=True, methods=["GET"], url_path="social-profile")
    def social_profile_livechat(self, request, pk, *args, **kwargs):
        data_redis = redis_client.get(f'{constants.COLLECT_LIVECHAT_SOCIAL_PROFILE}__{pk}')
        if not data_redis:
            return custom_response(200, "Get Social Profile LiveChat Error",[])
        res = ujson.loads(data_redis.decode('utf-8'))
        data_res = {
            "type": res.get('type'),
            "page": res.get('page'),
            "ip": res.get('ip'),
            "device": res.get('device'),
            "browser": res.get('browser'),
            "room_id": res.get('room_id')
        }
        return custom_response(200, "Get Social Profile LiveChat Successfully", data_res)
