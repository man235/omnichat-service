from sop_chat_service.app_connect.models import Message, Attachment
from core.utils.api_facebook_app import get_message_from_mid
from core.utils.format_message_for_websocket import facebook_format_mid
from django.utils import timezone
from core.schema import MessageChat
from core.schema import NatsChatMessage
from core.schema import FormatSendMessage


async def facebook_save_message_store_databases(room, msg: MessageChat):
    data_res = get_message_from_mid(room.page_id.access_token_page, msg.mid)
    data = facebook_format_mid(room, data_res)
    message = Message(
        room_id = room,
        fb_message_id = data.get("mid"),
        sender_id = data.get("sender_id"),
        recipient_id = data.get("recipient_id"),
        text = data.get("text"),
        uuid = msg.uuid
    )
    message.save()
    if data.get("attachments"):
        for attachment in data.get("attachments"):
            Attachment.objects.create(
                mid = message,
                type = attachment.get('type'),
                attachment_id = attachment.get('id'),
                url = attachment.get('url') if attachment.get('url') else attachment.get('video_url'),
                name = attachment.get('name'),
                size = attachment.get('size')
            )
    return


async def facebook_save_message_store_database(room, msg: NatsChatMessage):
    message = Message(
        room_id = room,
        fb_message_id = msg.mid,
        sender_id = msg.senderId,
        recipient_id = msg.recipientId,
        text = msg.text,
        uuid = msg.uuid,
        timestamp = msg.timestamp
    )
    message.save()
    if msg.attachments:
        for attachment in msg.attachments:
            Attachment.objects.create(
                mid = message,
                type = attachment.type,
                # attachment_id = attachment.get('id'),
                url = attachment.payloadUrl,
                name = attachment.name,
                size = attachment.size
            )
    return


async def facebook_send_message_store_database(room, _message: FormatSendMessage):
    message = Message(
        room_id = room,
        fb_message_id = _message.mid,
        sender_id = _message.sender_id,
        recipient_id = _message.recipient_id,
        text = _message.text,
        is_sender= True,
        is_seen = timezone.now(),
        uuid = _message.uuid
    )
    message.save()
    attachments = _message.attachments
    if attachments:
        for attachment in attachments:
            Attachment.objects.create(
                mid = message,
                type = attachment.type,
                attachment_id = attachment.id,
                url = attachment.url if attachment.url else attachment.video_url,
                name = attachment.name,
                size = attachment.size
            )
    return
