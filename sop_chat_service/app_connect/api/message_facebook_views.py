import asyncio
import nats
import json
import uuid
import logging
from core import constants
from django.conf import settings
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from sop_chat_service.app_connect.serializers.message_facebook_serializers import MessageFacebookSerializer
from sop_chat_service.app_connect.models import Message, Room
from core.utils.api_facebook_app import api_send_message_text_facebook, api_send_message_file_facebook, get_message_from_mid
from core.utils import facebook_format_data_from_mid_facebook
from sop_chat_service.app_connect.serializers.room_serializers import SearchMessageSerializer
from sop_chat_service.facebook.utils import custom_response
from django.utils import timezone
from django.db import connection

logger = logging.getLogger(__name__)


async def connect_nats_client_publish_websocket(new_topic_publish, data_mid):
    nats_client = await nats.connect(settings.NATS_URL)
    await nats_client.publish(new_topic_publish, bytes(data_mid))
    await nats_client.close()
    return

class MessageFacebookViewSet(viewsets.ModelViewSet):
    queryset = Room.objects.all()
    permission_classes = (permissions.AllowAny, )
    serializer_class = MessageFacebookSerializer

    @action(detail=False, methods=["POST"], url_path="send")
    def send_message(self, request, *args, **kwargs):
        serializer = MessageFacebookSerializer(data=request.data)
        room, data, message_type_attachment = serializer.validate(request ,request.data)
        # send message
        new_topic_publish = f'{constants.CHAT_SERVICE_TO_CORECHAT_PUBLISH}.{room.room_id}'
        if message_type_attachment:
            for file in data['files']:
                res = api_send_message_file_facebook(room.page_id.access_token_page, data, file)
                if not res:
                    return custom_response(400, "error", "Send message to Facebook error")
                message_response = get_message_from_mid(room.page_id.access_token_page, res['message_id'])
                _uuid = uuid.uuid4()
                data_mid_json = facebook_format_data_from_mid_facebook(room, message_response, _uuid)
                
                asyncio.run(connect_nats_client_publish_websocket(new_topic_publish, json.dumps(data_mid_json).encode()))
            msg = Message.objects.filter(room_id = room,is_seen__isnull = True).update(is_seen=timezone.now())
            return custom_response(200, "success", "Send message to Facebook success")
        else:
        # get message from mid
            res = api_send_message_text_facebook(room.page_id.access_token_page, data)
            if not res:
                return custom_response(400, "error", "Send message to Facebook error")
            message_response = get_message_from_mid(room.page_id.access_token_page, res['message_id'])
            _uuid = uuid.uuid4()
            data_mid_json = facebook_format_data_from_mid_facebook(room, message_response, _uuid)
            asyncio.run(connect_nats_client_publish_websocket(new_topic_publish, json.dumps(data_mid_json).encode()))
            msg = Message.objects.filter(room_id = room,is_seen__isnull = True).update(is_seen=timezone.now())
            return custom_response(200, "success", "Send message to Facebook success")
    @action(detail=False, methods=["POST"], url_path="search")
    def search_message(self, request,*args, **kwargs):
        sz = SearchMessageSerializer(data=request.data)
        room,search = sz.validate(request ,request.data)
        limit_req = 20
        offset_req = 0
        list_data= []
        result=[]
        if search and len(search.split(" ")) == 1:
            cursor = connection.cursor()
            cursor.execute('''
                    SELECT id
                    FROM  public.app_connect_message mes
                    WHERE un_accent(mes.text) ~* '\y%s\y' and mes.room_id_id = '%s'
            '''%(search,room.id))
            rows = cursor.fetchall()
            for row in rows:
                result.append(row)
            all_message = Message.objects.filter(room_id = room).count()
            if isinstance((all_message/limit_req),int):
                max_page =all_message/limit_req
            else:
                max_page = (all_message// limit_req)+1
            pagi=[]
            for item in result:
                count_msg=  Message.objects.filter(id__range=[1,item[0]],room_id=room).count()
                current_rank= all_message - count_msg
                if isinstance((current_rank/limit_req),int):
                    offset_req = current_rank/limit_req
                else:
                    offset_req = (current_rank// limit_req)+1
                if offset_req == 0:
                    offset_req = offset_req                
                search_data = {
                    "mid":item[0],
                    "page_size":limit_req,
                    "page":offset_req,
                }
                pagi.append(search_data)
            list_data= {
                "count": len(result),
                "max_page":max_page,
                "search_data":pagi
            }
        else:
            all_message = Message.objects.filter(room_id = room).count()
            id = []
            cursor = connection.cursor()
            cursor.execute('''
                    SELECT id
                    FROM  public.app_connect_message mes
                    WHERE un_accent(mes.text) ~* '\y%s\y' and mes.room_id_id = '%s'
            '''%(search,room.id))
            rows = cursor.fetchall()
            for row in rows:
                result.append(row)
            for item in result:
                id.append(item[0])
            for item in search.split(" "):
                cursor = connection.cursor()
                cursor.execute('''
                        SELECT id
                        FROM  public.app_connect_message mes
                        WHERE un_accent(mes.text) ~* '\y%s\y' and mes.room_id_id = '%s'
                '''%(item,room.id))
                rows = cursor.fetchall()
                for row in rows:
                    result.append(row)
                for item in result:
                    id.append(item[0])
            ids = set(id)
            if isinstance((all_message/limit_req),int):
                max_page =  all_message/limit_req
            else:
                max_page = (all_message// limit_req)+1
            
            pagi =[]
            for item_id  in ids :
                count_msg=  Message.objects.filter(id__range=[1,item_id],room_id=room).count()
                current_rank= all_message - count_msg
                if isinstance((current_rank/limit_req),int):
                    offset_req = current_rank/limit_req
                else:
                    offset_req = (current_rank// limit_req)+1
                if offset_req == 0:
                    offset_req = offset_req                
                search_data = {
                    "mid":item_id,
                    "page_size":limit_req,
                    "page":offset_req,
                }
                pagi.append(search_data)
            list_data= {
                "count": len(ids),
                "max_page":max_page,
                "search_data":pagi
            }     
        return custom_response(200,"success",list_data)
