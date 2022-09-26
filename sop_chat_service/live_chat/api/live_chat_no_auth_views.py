

from datetime import datetime, timedelta

from sop_chat_service.facebook.utils import custom_response

from ...app_connect.models import Room
from sop_chat_service.live_chat.models import LiveChat
from sop_chat_service.live_chat.api.serializer import CreateUserLiveChatSerializers, LiveChatSerializer, RoomLiveChatSerializer
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
import time
from iteration_utilities import unique_everseen



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
                print(room)
                sz = RoomLiveChatSerializer(room)
                print(sz.data)
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
        room = Room.objects.filter(external_id =x_cookie,type= 'live chat',room_message__is_sender = False,room_message__created_at__range = [start_date, end_date]).order_by("created_at").first()
        if room:  
            return custom_response(400,"Room is exist",[])
        else:
            new_room = Room.objects.create(type='livechat',external_id=x_cookie,name=x_cookie)
            user_info = data.get("user_info",None)
            if user_info:
                sz = CreateUserLiveChatSerializers(data=user_info,many=True)
                sz.is_valid(raise_exception=True)
                sz.save(room_id=new_room)
            return custom_response(200,"ok",[])
        