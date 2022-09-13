
from datetime import datetime

from sop_chat_service.facebook.utils import custom_response

from ..utils import Pagination
from ...app_connect.models import Attachment, Message, Room
from sop_chat_service.live_chat.models import LiveChat, LiveChatRegisterInfo
from sop_chat_service.live_chat.api.serializer import CreateUserLiveChatSerializers, GetMessageLiveChatSerializer, LiveChatSerializer, MessageLiveChatSerializer, RoomSerializer
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
import jwt



class LiveChatViewSet(viewsets.ModelViewSet):
    queryset = LiveChat.objects.all()
    serializer_class = LiveChatSerializer
    permission_classes = (permissions.AllowAny, )

    def list(self, request, *args, **kwargs):
        qs = LiveChat.objects.all()
        sz = LiveChatSerializer(qs, many=True)
        return custom_response(200,"Get Config Live Chat Successfully",sz.data)
    

    def create(self, request, *args, **kwargs):
        try:
            config = LiveChat.objects.all().first()
            data = request.data
            if config:
                if data:
                    data_config = data.get('live_chat', None)
                    update_config = LiveChatSerializer(config, data=data_config, partial=True)
                    update_config.is_valid(raise_exception=True)
                    update_config.save()
                    if data_config:
                        LiveChatRegisterInfo.objects.filter(live_chat_id=config).all().delete()
                        for item in data.get('registerinfor', None):
                            LiveChatRegisterInfo.objects.create(**item, live_chat_id=config)
                    
                    message= 'Update success'
                    
                return custom_response(200,message,[])
            else:
                if data:
                    data_config = data.get('live_chat', None)
                    if data_config:
                        live_chat = LiveChat.objects.create(**data_config)
                        for item in data.get('registerinfor', None):
                            LiveChatRegisterInfo.objects.create(**item, live_chat_id=live_chat)
                    
                    message= 'Create success'
                return custom_response(201,message,[])
        except Exception:
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def update(self, request, pk=None, *args, **kwargs):
        live_chat = self.get_object()
        data = request.data
        if request.data:
            if data['live_chat']:
                update = LiveChatSerializer(live_chat, data['live_chat'], partial=True)
                if data['registerinfor']:
                    LiveChatRegisterInfo.objects.filter(live_chat_id=live_chat).all().delete()
                    for item in data.get('registerinfor', None):
                        LiveChatRegisterInfo.objects.create(**item, live_chat_id=live_chat)
                    message= 'Update success'
                
            return custom_response(200,message,[])
        return Response(200, status=status.HTTP_200_OK)

    @action(detail=False, methods=["POST"], url_path="message/send")
    def send_message(self, request, *args):
        try:
            sz = MessageLiveChatSerializer(data=request.data)
            sz.is_valid(raise_exception=True)


            room = Room.objects.filter(type='Live Chat').order_by('-id').first()
            current_room = room
            if room:
                message = Message.objects.filter(room_id=room, is_sender=True).order_by('-created_at').first()
                if message:
                    a = message.created_at.strftime('%Y-%m-%d %H:%M:%S')
                    b = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    delta = (datetime.strptime(b, '%Y-%m-%d %H:%M:%S') -
                             datetime.strptime(a, '%Y-%m-%d %H:%M:%S')).total_seconds()
                    if delta/3600 > 24:
                        new_room = Room.objects.create( type='Live Chat')
                        current_room = new_room
                    else:
                        current_room = room
            else:
                new_room = Room.objects.create( type='Live Chat')
                current_room = new_room

            new_message = Message.objects.create(room_id=current_room, is_sender=True, sender_id=sz.validated_data.get(
                'sender_id'), recipient_id=sz.validated_data.get('recipient_id'), text=sz.validated_data.get('text'), created_at=datetime.now())
            attachments = request.FILES.getlist('attachments')
            for attachment in attachments:

                new_attachment = Attachment.objects.create(
                    file=attachment, type=attachment.content_type, mid=new_message)

            return Response(status=status.HTTP_200_OK)
        except Exception:
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    @action(detail=False,methods=['POST'],url_path='start')
    def start(self,request,*args, **kwargs):
        x_cookie = request.headers.get('X-Cookie')

        data = request.data
        room = Room.objects.create(type='livechat',external_id=x_cookie,name=x_cookie)
        sz = CreateUserLiveChatSerializers(data=data,many=True)
        sz.is_valid(raise_exception=True)
        sz.save(room_id=room)
        return custom_response(200,"ok",[])
        
    @action(detail=False, methods=["GET"], url_path="room", pagination_class=Pagination)
    def get_message(self, request, *args):
        room = request.query_params.get('room')
        qs = Message.objects.filter(room_id=room).order_by('-created_at')
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(qs, request)
        sz = GetMessageLiveChatSerializer(page, many=True)
        return paginator.get_paginated_response(sz.data)

    @action(detail=False, methods=["GET"], url_path="room")
    def get_room(self, request, *args, **kwargs):
        qs = Room.objects.filter(type='Live Chat', room_message__is_sender=False).order_by('-id')
        sz = RoomSerializer(qs, many=True)
        return Response(sz.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["POST"], url_path="room/")
    def create_room(self, request, *args):
        try:
            data = request.headers.get('X-Cookie')
            room = Room.objects.create(user_id=1,   type='Live Chat')
            message = {
                "message": "Create room success"
            }
            return Response(data=message, status=status.HTTP_200_OK)
        except Exception:
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class RoomViewSet(viewsets.ModelViewSet):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    permission_classes = (permissions.AllowAny, )

    def list(self, request, *args, **kwargs):
        qs = Room.objects.filter(room_message__is_sender=False).order_by('-created_at')
        sz = RoomSerializer(qs, many=True)
        return Response(sz.data, status=status.HTTP_200_OK)
