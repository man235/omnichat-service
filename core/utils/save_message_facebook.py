from sop_chat_service.app_connect.models import FanPage, Room, Message, UserApp
from .api_facebook_app import get_user_info
from django.utils import timezone
from asgiref.sync import sync_to_async

@sync_to_async
def save_message_store_database(room, data):
    message = Message(
        room_id = room,
        fb_message_id = data.get("mid"),
        sender_id = data.get("senderId"),
        recipient_id = data.get("recipientId"),
        text = data.get("text")
    )
    message.save()
    return


def send_and_save_message_store_database(room, data: dict):
    message = Message(
        room_id = room,
        fb_message_id = data.get("mid"),
        sender_id = data.get("senderId"),
        recipient_id = data.get("recipientId"),
        text = data.get("message")
    )
    message.save()
