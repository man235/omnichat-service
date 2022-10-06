

import asyncio
from datetime import datetime, timedelta
import json
import os
import uuid

from sop_chat_service.facebook.utils import custom_response
from sop_chat_service.live_chat.utils import connect_nats_client_publish_websocket, format_message, format_message_room, format_new_room

from ...app_connect.models import Attachment, Message, Room
from sop_chat_service.live_chat.models import LiveChat
from sop_chat_service.live_chat.api.serializer import CreateUserLiveChatSerializers, LiveChatSerializer, MessageLiveChatSend, RoomLiveChatSerializer
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
import time
from django.utils import timezone



class ChatViewSet(viewsets.ModelViewSet):
    
    queryset = LiveChat.objects.all()
    serializer_class = LiveChatSerializer
    permission_classes = (permissions.AllowAny, )

    @action(detail=False,methods=['GET'],url_path='message')
    def chat_message(self,request,*args, **kwargs):
        start_date=datetime.today() - timedelta(days=1)
        end_date=datetime.today()
        try:
            x_cookie = request.headers.get('X-Cookie')            
            room = Room.objects.filter(external_id =x_cookie,type= 'live chat',room_message__is_sender = False,room_message__created_at__range = [start_date, end_date]).order_by("created_at").first()
            if room:
                sz = RoomLiveChatSerializer(room)
                return custom_response(200,"ok",sz.data)
            else:
                return custom_response(200,"ok",[])
        except Exception:
            return custom_response(500,"INTERNAL_SERVER_ERROR",[])
    @action(detail=False,methods=['POST'],url_path='start')
    def start(self,request,*args, **kwargs):
        x_cookie = request.headers.get('X-Cookie')
        
        data = request.data
        start_date=datetime.today() - timedelta(days=1)
        end_date=datetime.today()
        if not data.get("live_chat_id",None):
            return custom_response(400,"live_chat_id is required",[])
        room = Room.objects.filter(external_id =x_cookie,type= 'live chat',room_message__is_sender = False,room_message__created_at__range = [start_date, end_date]).exclude(status = "completed").order_by("created_at").first()
        if room:  
            return custom_response(400,"Room is exist",[])
        else:
            live_chat = LiveChat.objects.filter(id =data.get("live_chat_id",None)).first()
            if not live_chat:
                return custom_response(400,"live chat is valid",[])
            user_id = live_chat.user_id
            new_room = Room.objects.create(type='livechat',external_id=x_cookie,user_id=user_id,room_id=uuid.uuid4(),approved_date=timezone.now())
            room_id = new_room.id
            if live_chat.is_start_message:
                Message.objects.create(room_id=new_room, is_sender=False, sender_id=x_cookie, text=live_chat.start_message, uuid=uuid.uuid4(),created_at=datetime.now(),timestamp=int(time.time()))
            user_info = data.get("user_info",None)
            if user_info:
                sz = CreateUserLiveChatSerializers(data=user_info,many=True)
                sz.is_valid(raise_exception=True)
                sz.save(room_id=new_room)
            new_topic_publish = f'live-chat-action-room.{user_id}'
            data_message = format_new_room(new_room)
            asyncio.run(connect_nats_client_publish_websocket(new_topic_publish, json.dumps(data_message).encode()))
            return custom_response(200,"ok",[])
    
    def retrieve(self, request, pk=None):    
        qs = LiveChat.objects.filter(id = pk)
        sz = LiveChatSerializer(qs, many=True)
        data = {
            "user_info":{
                "name":"",
                "avatar":""
            },
            "config":sz.data
        }
        return custom_response(200,"Get Config Live Chat Successfully",data)
    @action(detail=False, methods=["POST"], url_path="send-message")
    def send_chat_message(self, request, *args):
        # user_header = get_user_from_header(request.headers)
        x_cookie = request.headers.get('X-Cookie')

        sz = MessageLiveChatSend(data=request.data, context={"request": request})
        sz.is_valid(raise_exception=True)
        try:
            room_id = sz.data['room_id']
            room = Room.objects.filter(room_id = room_id).first()
            user_id = room.user_id
            new_topic_publish = f'live-chat-room.{room_id}'
            
            live_chat_action_room = f'live-chat-action-room.{user_id}'
            data_message={}
            if sz.data.get("mid"):
                message = Message.objects.get(id = sz.data.get("mid"))
                new_message = Message.objects.create(room_id=room,mid =message, is_sender=False, sender_id=x_cookie, text=sz.data.get('message_text'), uuid=uuid.uuid4(),created_at=datetime.now(),timestamp=int(time.time()))
                attachments = request.FILES.getlist('file')
                for attachment in attachments:
                    new_attachment = Attachment.objects.create( 
                        file=attachment, type=attachment.content_type, mid=new_message)
                data_message = format_message(new_message)
                asyncio.run(connect_nats_client_publish_websocket(live_chat_action_room, json.dumps(data_message).encode()))

            else:
                new_message = Message.objects.create(room_id=room,is_sender=False, sender_id=x_cookie, text=sz.data.get('message_text'), uuid=uuid.uuid4(),created_at=datetime.now(),timestamp=int(time.time()))
                attachments = request.FILES.getlist('file')
                for attachment in attachments:
                    new_attachment = Attachment.objects.create(
                        file=attachment, type=attachment.content_type, mid=new_message)
                data_message = format_message(new_message)
                asyncio.run(connect_nats_client_publish_websocket(live_chat_action_room, json.dumps(data_message).encode()))
            data_message = format_message_room(room)
            asyncio.run(connect_nats_client_publish_websocket(new_topic_publish, json.dumps(data_message).encode()))
            return custom_response(200,"ok",[])
        except Exception:
            return custom_response(500,"INTERNAL_SERVER_ERROR",[])
