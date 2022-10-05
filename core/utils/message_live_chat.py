from asgiref.sync import sync_to_async
from sop_chat_service.app_connect.serializers.message_serializers import MessageSerializer
@sync_to_async
def message_store_database(message):
    sz = MessageSerializer(message,many=True)
    return sz.data
