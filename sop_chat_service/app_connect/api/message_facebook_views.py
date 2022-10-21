import asyncio
import nats
import json
import uuid
import logging
from core import constants
from django.conf import settings
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from sop_chat_service.app_connect.serializers.message_facebook_serializers import MessageFacebookSerializer
from sop_chat_service.app_connect.models import Message, Room
from core.utils.api_facebook_app import api_send_message_text_facebook, api_send_message_file_facebook, get_message_from_mid
from core.utils import facebook_format_data_from_mid_facebook
from sop_chat_service.app_connect.serializers.message_serializers import MessageSerializer, ResultMessageSerializer
from sop_chat_service.app_connect.serializers.room_serializers import SearchMessageSerializer, SortMessageSerializer
from sop_chat_service.facebook.utils import custom_response
from django.utils import timezone

from sop_chat_service.utils.pagination_data import pagination_list_data, pagination_message


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
            room.is_seen = timezone.now()
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
            room.is_seen = timezone.now()
            return custom_response(200, "success", "Send message to Facebook success")
    @action(detail=False, methods=["POST"], url_path="search")
    def search_message(self, request,*args, **kwargs):
        sz = SearchMessageSerializer(data=request.data,many=False)
        limit_req = request.data.get('limit', 20)
        offset_req = request.data.get('offset', 1)
        list_data= []
        if sz.is_valid(raise_exception=True):
            if sz.data.get('search'):
                message = Message.objects.filter(text__icontains= sz.data.get('search'))
                message_sz = ResultMessageSerializer(message,many=True)
                list_data = list(message_sz.data)
        data_result = pagination_list_data(list_data, limit_req, offset_req)
        return custom_response(200,"success",data_result)
    
    def retrieve(self, request, pk=None):
        message=Message.objects.filter(id=pk).first()
        result = Message.objects.filter(room_id=message.room_id).order_by("-created_at")
        count_msg=  Message.objects.filter(id__range=[1,pk],room_id=message.room_id).count()
        sz= MessageSerializer(result, many=True)
        limit_req = 20
        offset_req = 0
        if isinstance((count_msg/limit_req),int):
            offset_req = count_msg/limit_req
        else:
            offset_req = (count_msg// limit_req)+1
        if offset_req == 0:
            offset_req = offset_req
        if isinstance((len(sz.data)/limit_req),int):
            max_page = len(sz.data)/limit_req
        else:
            max_page = (len(sz.data)// limit_req)+1
        list_data = {
            "page_size":limit_req,
            "page":offset_req,
            "max_page":max_page,
            "count": len(sz.data),
        }
        return custom_response(200,"ok",list_data)
