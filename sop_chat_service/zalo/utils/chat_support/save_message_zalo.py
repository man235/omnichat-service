from logging import Logger
from typing import Any
from core.schema.message_receive import ChatOptional
from sop_chat_service.app_connect.models import Message, Attachment, Room
from django.utils import timezone
from core.schema import MessageWebSocket
from sop_chat_service.utils.storages import upload_file_to_minio
from django.conf import settings
import uuid
import logging

logger = logging.getLogger(__name__)

async def save_message_store_database_zalo(
    room,
    msg: MessageWebSocket,
    optionals: list[ChatOptional] = None
) -> None:
    
    message = Message(
        room_id = room,
        fb_message_id = msg.mid,
        sender_id = msg.sender_id,
        recipient_id = msg.recipient_id,
        text = msg.text,
        sender_name = room.name,
        created_at = str(timezone.now()),
        uuid = msg.uuid,
    )
    message.save()
    
    if msg.attachments:
         for index, attachment in enumerate(msg.attachments):
            if not optionals[index] and not optionals[index].data.get('attachments'):
                attachment_name = None
                attachment_size = None
                pass
            else:
                optional_attachment_payload = optionals[index].data.get('attachments')[index].get('payload')
                attachment_name = optional_attachment_payload.get('name')
                attachment_size = optional_attachment_payload.get('size')
            
            Attachment.objects.create(
                mid = message,
                type = attachment.type,
                attachment_id = optional_attachment_payload.get('id'),
                url = attachment.url,
                name = attachment_name,
                size = attachment_size
            )

def store_sending_message_database_zalo(
    room: Room,
    mid: str = None,
    sender_id: str = None, 
    recipient_id: str = None,
    text: str = None,
    attachment: Any = None,
    attachment_type: str = None,
) -> None:
        
    message = Message(
        room_id = room,
        fb_message_id = mid,
        sender_id = sender_id,
        recipient_id = recipient_id,
        text = text,
        is_sender= True,
        is_seen = str(timezone.now()),
        uuid = str(uuid.uuid4()),
        created_at = str(timezone.now()),
    )
    message.save()
    
    if attachment:
        domain = settings.DOMAIN_MINIO_SAVE_ATTACHMENT
        sub_url = f"api/live_chat/chat_media/get_chat_media?name=live_chat_room_{room.room_id}/"
        data_upload_file = upload_file_to_minio(attachment, room.id)
        logger.debug(f"ATTACHMENT {data_upload_file} +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ ")

        new_attachment = Attachment.objects.create(
            file=data_upload_file,
            type=attachment.content_type,
            name=attachment.name,
            url = str(domain+sub_url) + str(data_upload_file)
        )
        
    return new_attachment
