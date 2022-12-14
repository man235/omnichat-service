from typing import Any, List
from core.schema.message_receive import ChatOptional
from sop_chat_service.app_connect.models import Message, Attachment, Room
from django.utils import timezone
from core.schema import MessageChat
from sop_chat_service.utils.storages import upload_file_to_minio
from sop_chat_service.zalo.utils.chat_support.format_message_zalo import format_atachment_type_from_zalo_message
from sop_chat_service.zalo.utils.chat_support.type_constant import FILE_CONTENT_TYPE, FILE_DOC_EXTENSION, FILE_MESSAGE, FILE_MSWORD_EXTENSION
from django.conf import settings
from core import constants
import uuid
import logging

logger = logging.getLogger(__name__)


async def save_msg_store_database_zalo(
    room,
    msg: MessageChat,
    optionals: List[ChatOptional] = None
) -> None:
    for _room in room:
        message = Message(
            room_id = _room,
            fb_message_id = msg.mid,
            sender_id = msg.sender_id,
            recipient_id = msg.recipient_id,
            text = msg.text,
            sender_name = _room.name,
            created_at = str(timezone.now()),
            uuid = msg.uuid,
        )
        message.save()
        
        if msg.attachments:
            for index, attachment in enumerate(msg.attachments):
                if optionals[index] and optionals[index].data.get('attachments'):
                    optional_attachment = optionals[index].data.get('attachments')[index]
                    optional_attachment_payload = optional_attachment.get('payload')
                    attachment_type = optional_attachment.get('type')
                    attachment_name = optional_attachment_payload.get('name')
                    attachment_id = optional_attachment_payload.get('id')
                    attachment_size = optional_attachment_payload.get('size')
                    attachment_file_type = optional_attachment_payload.get('type')

                    # Reformat file type
                    if attachment_type == FILE_MESSAGE:
                        if None is not attachment_file_type in FILE_DOC_EXTENSION:
                            reformatted_attachment_type = '/'.join([
                                FILE_CONTENT_TYPE,
                                FILE_MSWORD_EXTENSION
                            ])
                        else:
                            reformatted_attachment_type = '/'.join([
                                FILE_CONTENT_TYPE,
                                attachment_file_type
                            ])
                    else:
                        reformatted_attachment_type = attachment.type   # except "file", such as: "image", "gif"
                else:
                    # Don't have optionals
                    reformatted_attachment_type,
                    attachment_name,
                    attachment_size,
                    attachment_id = None

                Attachment.objects.create(
                    mid=message,
                    type=reformatted_attachment_type,
                    attachment_id=attachment_id,
                    url=attachment.url,
                    name=attachment_name,
                    size=attachment_size
                )


async def save_message_store_database_zalo(
    room,
    msg: MessageChat,
    optionals: List[ChatOptional] = None
) -> None:
    message = Message(
        room_id=room,
        fb_message_id=msg.mid,
        sender_id=msg.sender_id,
        recipient_id=msg.recipient_id,
        text=msg.text,
        sender_name=room.name,
        created_at=str(timezone.now()),
        uuid=msg.uuid,
        timestamp=msg.timestamp
    )
    message.save()
    
    if msg.attachments:
        for index, attachment in enumerate(msg.attachments):
            if optionals[index] and optionals[index].data.get('attachments'):
                reformatted_attachment_type, \
                attachment_name, \
                attachment_size, \
                attachment_id = format_atachment_type_from_zalo_message(attachment, optionals, index)
                                
            Attachment.objects.create(
                mid=message,
                type=reformatted_attachment_type,
                attachment_id=attachment_id,
                url=attachment.url,
                name=attachment_name,
                size=attachment_size
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
        room_id=room,
        fb_message_id=mid,
        sender_id=sender_id,
        recipient_id=recipient_id,
        text=text,
        is_sender=True,
        is_seen=str(timezone.now()),
        uuid=str(uuid.uuid4()),
        created_at=str(timezone.now()),
    )
    message.save()
    
    if attachment:
        try:
            domain = settings.DOMAIN_MINIO_SAVE_ATTACHMENT
            sub_url = f"api/live_chat/chat_media/get_chat_media?name={constants.ZALO_ROOM_MINIO}_{room.room_id}/"
            data_upload_file = upload_file_to_minio(attachment, room.room_id, constants.ZALO_ROOM_MINIO)    # may be 70 second timeout
            new_attachment = Attachment.objects.create(
                mid = message,
                file=data_upload_file,
                type=attachment_type,
                name=attachment.name,
                url=str(domain+sub_url)+str(data_upload_file),
                size=attachment.size
            )
            logger.debug(f"SENDED ATTACHMENTS {new_attachment.name} ++++++++++++++++++++++++++++++++++++++++++++++++++++++++ ")
            return new_attachment
        except Exception as e:
            return None

    return None
