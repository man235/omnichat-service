from sop_chat_service.app_connect.models import Message, Attachment
from asgiref.sync import sync_to_async
from django.utils import timezone
from core.schema import MessageWebSocket

@sync_to_async
def save_message_store_database_zalo(room, msg: MessageWebSocket):
    # data_res = get_message_from_mid(room.page_id.access_token_page, data_msg.get("mid"))
    # data = format_data_from_facebook_nats_subscribe(room, data_res, data_msg)
    message = Message(
        room_id = room,
        fb_message_id = msg.mid,
        sender_id = msg.sender_id,
        recipient_id = msg.recipient_id,
        text = msg.text,
        sender_name = room.name,
        uuid = msg.uuid
    )
    message.save()
    if msg.attachments:
        for attachment in msg.attachments:
            Attachment.objects.create(
                mid = message,
                type = attachment.type,
                # attachment_id = attachment.get('id'),
                url = attachment.payloadUrl,
                # name = attachment.get('name'),
                # size = attachment.get('size')
            )
            
    return


def send_and_save_message_store_database(room, data: dict, uuid):
    message = Message(
        room_id = room,
        fb_message_id = data.get("mid"),
        sender_id = data.get("sender_id"),
        recipient_id = data.get("recipient_id"),
        text = data.get("text"),
        is_sender= True,
        is_seen = timezone.now(),
        uuid = uuid
    )
    message.save()
    attachments = data.get("attachments")
    if attachments:
        for attachment in attachments:
            Attachment.objects.create(
                mid = message,
                type = attachment.get('type'),
                attachment_id = attachment.get('id'),
                url = attachment.get('url') if attachment.get('url') else attachment.get('video_url'),
                name = attachment.get('name'),
                size = attachment.get('size')
            )
    return
