from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ValidationError
import nats
from django.conf import settings

from sop_chat_service.app_connect.serializers.message_serializers import MessageSerializer
from sop_chat_service.app_connect.serializers.room_serializers import FormatRoomSerializer, RoomSerializer
import asyncio

class Pagination(PageNumberPagination):
    page_size = 1
    page_size_query_param = 'page_size'
    max_page_size = 30

    def get_paginated_response(self, data):
        return Response({
            'links': {
                'next': self.get_next_link(),
                'previous': self.get_previous_link()
            },
            'count': self.page.paginator.count,
            'page_size': self.page_size,
            'data': data
        }, status=status.HTTP_200_OK)
def file_size(value): # add this to some file where you can import it from
        limit = 5 * 1024 * 1024
        if value.size > limit:
            raise ValidationError('File too large. Size should not exceed 5 MB.')
        
async def connect_nats_client_publish_websocket(new_topic_publish, data_mid):
   
    nats_client = await nats.connect(settings.NATS_URL)
    await nats_client.publish(new_topic_publish, bytes(data_mid))

    await nats_client.close()
    return
def format_message_room(data):
    sz = FormatRoomSerializer(data,many=False)
    return {
        "events":"new_message",
        "data":sz.data
        }
def format_message(data):
    sz = MessageSerializer(data,many=False)
    return {
        "events":"new_last_message",
        "data":sz.data
        }
def format_room(data):
    sz = RoomSerializer(data, many=False)
    return {
        "events":"completed_room",
        "data":sz.data
        }
def format_new_room(data):
    sz = RoomSerializer(data, many=False)
    return {
        "events":"new_room",
        "data":sz.data
        }