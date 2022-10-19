from typing import Any
from sop_chat_service.app_connect.models import Message, Attachment, Room
from django.utils import timezone
from sop_chat_service.utils.storages import upload_file_to_minio
from sop_chat_service.zalo.utils.chat_support.type_constant import FILE_CONTENT_TYPE, FILE_DOC_EXTENSION, FILE_MESSAGE, FILE_MSWORD_EXTENSION
from django.conf import settings
import logging
from core.schema import FormatSendMessage

logger = logging.getLogger(__name__)


async def zalo_send_message_store_database(room: Room, _message: FormatSendMessage):
    message = Message(
        room_id=room,
        fb_message_id=_message.mid,
        sender_id=_message.sender_id,
        recipient_id=_message.recipient_id,
        text=_message.text,
        is_sender=True,
        is_seen=str(timezone.now()),
        uuid=_message.uuid,
        created_at=str(timezone.now()),
    )
    message.save()
    if _message.attachments:
        try:
            domain = settings.DOMAIN_MINIO_SAVE_ATTACHMENT
            sub_url = f"api/live_chat/chat_media/get_chat_media?name=live_chat_room_{room.room_id}/"
            data_upload_file = upload_file_to_minio(_message.attachments, room.id)    # may be 70 second timeout
            logger.debug(f"SENDED ATTACHMENTS {data_upload_file} +++++++++++++++ ")
            new_attachment = Attachment.objects.create(
                file=data_upload_file,
                type=_message.attachments.type,
                name=_message.attachments.name,
                url=str(domain+sub_url)+str(data_upload_file)
            )
            return new_attachment
        except Exception as e:
            return None
    return None
