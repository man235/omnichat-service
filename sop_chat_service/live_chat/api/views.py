
from datetime import datetime

from sop_chat_service.facebook.utils import custom_response

from ..utils import Pagination
from ...app_connect.models import Attachment, Message, Room
from sop_chat_service.live_chat.models import LiveChat, LiveChatRegisterInfo
from sop_chat_service.live_chat.api.serializer import CreateUserLiveChatSerializers, GetMessageLiveChatSerializer, LiveChatSerializer, MessageLiveChatSerializer, RoomSerializer
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
import time



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
                        if data.get('registerinfo', None):
                            for item in data.get('registerinfo', None):
                                LiveChatRegisterInfo.objects.create(**item, live_chat_id=config)
                    message= 'Update success'
                    
                return custom_response(200,message,[])
            else:
                if data:
                    data_config = data.get('live_chat', None)
                    if data_config:
                        if data.get('registerinfo', None):
                            live_chat = LiveChat.objects.create(**data_config)
                            for item in data.get('registerinfo', None):
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
                update.is_valid(raise_exception=True)
                update.save()
                if data.get('registerinfo', None):
                    LiveChatRegisterInfo.objects.filter(live_chat_id=live_chat).all().delete()
                    for item in data.get('registerinfo', None):
                        LiveChatRegisterInfo.objects.create(**item, live_chat_id=live_chat)
                    message= 'Update success'
                
            return custom_response(200,message,[])
        return Response(200, status=status.HTTP_200_OK)

    @action(detail=False, methods=["POST"], url_path="message/send")
    def send_message(self, request, *args):
        x_cookie = request.headers.get('X-Cookie')

        try:
            sz = MessageLiveChatSerializer(data=request.data)
            sz.is_valid(raise_exception=True)
            room = Room.objects.filter(type='Live Chat',external_id=x_cookie).order_by('-id').first()
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
                new_room = Room.objects.create(type='Live Chat',external_id=x_cookie)
                current_room = new_room

            new_message = Message.objects.create(room_id=current_room, is_sender=True, sender_id=sz.validated_data.get(
                'sender_id'), recipient_id=sz.validated_data.get('recipient_id'), text=sz.validated_data.get('text'), created_at=datetime.now(),timestamp=int(time.time()))
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
        
    @action(detail=False, methods=["GET"], url_path="active")
    def active(self,request,*args, **kwargs):
        id = request.data.get("id",None)
        active = request.data("active",None)
        
        live_chat = LiveChat.objects.filter(id = id).first()
        if active:
            live_chat.is_active = True
        else:
            live_chat.is_active =False
        return custom_response(200,"Active Live Chat Successfully",[])

