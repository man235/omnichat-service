from sop_chat_service.app_connect.models import Message, Attachment
from core.utils.api_facebook_app import get_message_from_mid
from core.utils.format_message_for_websocket import format_data_from_facebook
from asgiref.sync import sync_to_async
from django.utils import timezone


@sync_to_async
def save_message_store_database(room, data):
    data_res = get_message_from_mid(room.page_id.access_token_page, data.get("mid"))
    data = format_data_from_facebook(room, data_res)
    message = Message(
        room_id = room,
        fb_message_id = data.get("mid"),
        sender_id = data.get("sender_id"),
        recipient_id = data.get("recipient_id"),
        text = data.get("text")
    )
    message.save()
    if data.get("attachments"):
        for attachment in data.get("attachments"):
            Attachment.objects.create(
                mid = message,
                type = attachment['type'],
                url = attachment['url'],
                name = attachment['name'],
                size = attachment['size']
            )
    return


def send_and_save_message_store_database(room, data: dict):
    message = Message(
        room_id = room,
        fb_message_id = data.get("mid"),
        sender_id = data.get("senderId"),
        recipient_id = data.get("recipientId"),
        text = data.get("text"),
        is_sender= True,
        is_seen = timezone.now()
    )
    message.save()
    attachments = data.get("attachments")
    if attachments:
        for attachment in attachments:
            Attachment.objects.create(
                mid = message,
                type = attachment['type'],
                url = attachment['url'],
                attachment_id = attachment['id'],
                name = attachment['name'],
                size = attachment['size']
            )
    return
