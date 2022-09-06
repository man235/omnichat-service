from sop_chat_service.app_connect.models import FanPage, Room, Message
from typing import Dict
import datetime
from django.utils import timezone
from asgiref.sync import sync_to_async

@sync_to_async
def save_message_store_database(data: dict):
    check_fanpage_activate = FanPage.objects.filter(page_id=data.get("recipientId")).first()
    if not check_fanpage_activate or not check_fanpage_activate.is_active:
        return
    check_room = Room.objects.filter(page_id=check_fanpage_activate.id, external_id=data['senderId']).first()
    if not check_room or check_room.completed_date:
        new_room = Room(
            page_id = check_fanpage_activate,
            external_id = data['recipientId'],
            user_id = data.get("senderId"),        # User SSO
            # name = user_app.name,
            approved_date = timezone.now(),
            type = "facebook",
            completed_date = None,
            conversation_id = ""
        )
        new_room.save()

        message = Message(
            room_id = new_room,
            fb_message_id = data.get("mid"),
            sender_id = data.get("senderId"),
            recipient_id = data.get("recipientId"),
            text = data.get("text"),
            # created_at = datetime.datetime.now()
        )
        message.save()
        return
    elif not check_room.completed_date:
        message = Message(
            room_id = check_room,
            fb_message_id = data.get("mid"),
            sender_id = data.get("senderId"),
            recipient_id = data.get("recipientId"),
            text = data.get("text"),
            # sender_name = data.get("mid"),
            # created_at = datetime.datetime.now()
        )
        message.save()
        return

# @sync_to_async
def send_and_save_message_store_database(data: dict):
    check_fanpage_activate = FanPage.objects.filter(page_id=data.get("senderId")).first()
    if not check_fanpage_activate or not check_fanpage_activate.is_active:
        return
    check_room = Room.objects.filter(page_id=check_fanpage_activate.id, external_id=data['recipientId']).first()
    if not check_room or check_room.completed_date:
        new_room = Room(
            page_id = check_fanpage_activate,
            external_id = data['recipientId'],
            user_id = data.get("senderId"),        # User SSO
            # name = user_app.name,
            approved_date = timezone.now(),
            type = "facebook",
            completed_date = None,
            conversation_id = ""
        )
        new_room.save()

        message = Message(
            room_id = new_room,
            fb_message_id = data.get("mid"),
            sender_id = data.get("senderId"),
            recipient_id = data.get("recipientId"),
            text = data.get("message"),
            # created_at = datetime.datetime.now()
        )
        message.save()
        return
    elif not check_room.completed_date:
        message = Message(
            room_id = check_room,
            fb_message_id = data.get("mid"),
            sender_id = data.get("senderId"),
            recipient_id = data.get("recipientId"),
            text = data.get("message"),
            # sender_name = data.get("mid"),
            # created_at = datetime.datetime.now()
        )
        message.save()
        return
