
from datetime import datetime, timedelta

from sop_chat_service.facebook.utils import custom_response

from ..utils import Pagination
from ...app_connect.models import Attachment, Message, Room
from sop_chat_service.live_chat.models import LiveChat, LiveChatRegisterInfo
from sop_chat_service.live_chat.api.serializer import CreateUserLiveChatSerializers, GetMessageLiveChatSerializer, LiveChatSerializer, MessageLiveChatSend, MessageLiveChatSerializer, RoomSerializer, UpdateAvatarLiveChatSerializer
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
import time
from iteration_utilities import unique_everseen



class LiveChatViewSet(viewsets.ModelViewSet):

    queryset = LiveChat.objects.all()
    serializer_class = LiveChatSerializer
    permission_classes = (permissions.AllowAny, )

    def list(self, request, *args, **kwargs):
        auth_id = request.headers.get('X-Auth-Id')
        qs = LiveChat.objects.filter(user_id = auth_id)
        sz = LiveChatSerializer(qs, many=True)
        return custom_response(200,"Get Config Live Chat Successfully",sz.data)
    

    def create(self, request, *args, **kwargs):
        auth_id = request.headers.get('X-Auth-Id')
        try:
            config = LiveChat.objects.filter(user_id = auth_id).first()
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
                    message= 'Update success'
                    return custom_response(200,message,config.id)
            else:
                if data:
                    data_config = data.get('live_chat', None)
                    if data_config:
                        live_chat = LiveChat.objects.create(**data_config,user_id = auth_id)
                        if data.get('registerinfo', None):
                            for item in data.get('registerinfo', None):
                                LiveChatRegisterInfo.objects.create(**item, live_chat_id=live_chat)
                        message= 'Create success'
                        return custom_response(200,message,live_chat.id)
        except Exception:
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def update(self, request, pk=None, *args, **kwargs):
        live_chat = self.get_object()
        data = request.data
        if request.data:
            if data['avatar']:
                update = UpdateAvatarLiveChatSerializer(live_chat,data=request.data)
                update.is_valid(raise_exception=True)
                update.save()
                message= 'Update success'
            return custom_response(200,message,[])
        return Response(200, status=status.HTTP_200_OK)
    @action(detail=False, methods=["GET"], url_path="room")
    def room(self, request, *args):
        auth_id = request.headers.get('X-Auth-Id')
        start_date=datetime.today() - timedelta(days=1)
        end_date=datetime.today()
        try:
            rooms = Room.objects.filter(user_id =auth_id,type= 'live chat',room_message__is_sender = False).exclude(room_message__created_at__range = [start_date, end_date])
            if rooms:
                for room in unique_everseen(rooms):
                    Room.objects.filter(id = room.id).update(status="expired")
                return custom_response(200,"ok",[])
        except Exception:
            return custom_response(500,"INTERNAL_SERVER_ERROR",[])
    @action(detail=False, methods=["POST"], url_path="message")
    def send_message(self, request, *args):
        auth_id = request.headers.get('X-Auth-Id')
        try:
            sz = MessageLiveChatSend(data=request.data)
            sz.is_valid(raise_exception=True)
            room = Room.objects.filter(id = sz.room_id).first()
            if sz.data.get("mid"):
                message = Message.objects.get(id = sz.data.get("mid"))
                new_message = Message.objects.create(room_id=room,mid =message, is_sender=True, sender_id=auth_id, text=sz.data.get('text'), created_at=datetime.now(),timestamp=int(time.time()))
                attachments = request.FILES.getlist('file')
                for attachment in attachments:
                    new_attachment = Attachment.objects.create(
                        file=attachment, type=attachment.content_type, mid=new_message)
            else:
                new_message = Message.objects.create(room_id=room,mid =message, is_sender=True, sender_id=auth_id, text=sz.data.get('text'), created_at=datetime.now(),timestamp=int(time.time()))
                attachments = request.FILES.getlist('file')
                for attachment in attachments:
                    new_attachment = Attachment.objects.create(
                        file=attachment, type=attachment.content_type, mid=new_message)
            return custom_response(200,"ok",[])
        except Exception:
            return custom_response(500,"INTERNAL_SERVER_ERROR",[])


    
  