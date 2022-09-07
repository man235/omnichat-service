from django.conf import settings
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from sop_chat_service.app_connect.serializers.message_facebook_serializers import MessageFacebookSerializer
from sop_chat_service.app_connect.models import Room
from core.utils.api_facebook_app import api_send_message_text_facebook, api_send_message_file_facebook, get_message_from_mid
from core.utils import save_message_store_database, send_and_save_message_store_database
import asyncio
import nats
from django.conf import settings


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
        if message_type_attachment:
            res = api_send_message_file_facebook(room.page_id.access_token_page, data)
        else:
            res = api_send_message_text_facebook(room.page_id.access_token_page, data)
        # get message from mid
        if not res:
            return Response(False, status=status.HTTP_400_BAD_REQUEST)
        message_response = get_message_from_mid(room.page_id.access_token_page, res['message_id'])
        data_mid_json = {
            "message": message_response['message'],
            "created_time": message_response['created_time'],
            "senderId": message_response['from']['id'],
            "recipientId": message_response['to']['data'][0]['id'],
            "attachments": message_response.get('attachments').get('data') if message_response.get('attachments') else None,
            "room_id": room.id,
            "is_sender": True
        }
        attachments = []
        if message_response.get('attachments'):
            attachments = [{
                "id": message_response.get('attachments').get('data')[0]['id'],
                "mime_type": message_response.get('attachments').get('data')[0]['mime_type'],
                "name": message_response.get('attachments').get('data')[0]['name'],
                "url": message_response.get('attachments').get('data')[0]['image_data']['url']
            }]
            
        data_mid = """{
            "message": "%s",
            "created_time": "%s",
            "senderId": "%s",
            "recipientId": "%s",
            "attachments": "%s",
            "is_sender": "%s"
        }""" %(
            message_response['message'],
            message_response['created_time'],
            message_response['from']['id'],
            message_response['to']['data'][0]['id'],
            attachments,
            True
        )
        new_topic_publish = f'message_{room.room_id}'
        asyncio.run(connect_nats_client_publish_websocket(new_topic_publish, data_mid.encode('utf-8')))
        send_and_save_message_store_database(room, data_mid_json)
        return Response(True, status=status.HTTP_200_OK)
