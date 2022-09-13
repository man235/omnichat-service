from sop_chat_service.app_connect.models import Message, Attachment
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
    if data.get("attachments"):
        Attachment.objects.create(
            mid = message,
            type = data.get("attachments")[0]['type'],
            url = data.get("attachments")[0]['payloadUrl']
        )
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
    if data.get("attachments"):
        Attachment.objects.create(
            mid = message,
            type = data.get("attachments")[0]['mime_type'],
            url = data.get("attachments")[0]['image_data']['url'],
            attachment_id = data.get("attachments")[0]['id']
        )
    return
