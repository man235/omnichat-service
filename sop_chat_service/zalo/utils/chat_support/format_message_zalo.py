from typing import Any, List
from django.utils import timezone
from core import constants
from sop_chat_service.zalo.utils.chat_support.type_constant import (
    FILE_CONTENT_TYPE,
    FILE_CONTENT_TYPE_TEXT,
    FILE_CSV_TYPE,
    FILE_DOC_EXTENSION,
    FILE_MESSAGE,
    FILE_MSWORD_EXTENSION,
    FILE_PDF_TYPE,
    IMAGE_MESSAGE
)
import uuid


def format_sended_message_to_socket(
    text: str = None,
    attachments: List[Any] = [],
    msg_id: str = None,
    oa_id: str = None,
    recipient_id: str = None,
    room_room_id: str = None,
    room_id: str = None,
    user_id: str = None,    
) -> dict:
    return {
        "mid": msg_id,
        "attachments": attachments,
        "text": text,
        "created_time": str(timezone.now()),
        "sender_id": oa_id,
        "recipient_id": recipient_id,
        "room_id": room_room_id,
        "id": room_id,
        "is_sender": True,
        "created_at": str(timezone.now()),
        "is_seen": None,
        "message_reply": None,
        "reaction": None,
        "reply_id": None,
        "sender_name": None,
        "uuid": str(uuid.uuid4()),
        "msg_status": constants.SEND_MESSAGE_STATUS,
        "user_id": user_id,
        "event": constants.SIO_EVENT_ACK_MSG_SALEMAN_TO_CUSTOMER,
        "type": constants.ZALO
    }
    
    
def format_attachment_type(attachment: Any) -> str:
    attachment_content_type = attachment.content_type
    
    if attachment_content_type:
        attachment_base_type = attachment_content_type.split('/')[0]
        if attachment_base_type:
            if attachment_base_type == FILE_CONTENT_TYPE or attachment_base_type == FILE_CONTENT_TYPE_TEXT:
                attachment_type = FILE_MESSAGE
            elif attachment_base_type == IMAGE_MESSAGE:
                attachment_type = IMAGE_MESSAGE
        return attachment_type
    else:
        return IMAGE_MESSAGE
        

def reformat_attachment_type(attachment: Any) -> str:
    reformatted_attachment_type = None
    attachment_content_type = str(attachment.content_type)  # application/docx   
    attachment_base_type = attachment_content_type.split('/')[0]
    attachment_extension_type = attachment_content_type.split('/')[1]
    attachment_name: str = attachment.name
    attachment_extension_name = attachment_name.split('.')[-1]
    
    if attachment_base_type == FILE_CONTENT_TYPE or attachment_base_type == FILE_CONTENT_TYPE_TEXT:    # application
        if attachment_extension_name in FILE_DOC_EXTENSION:     
            reformatted_attachment_type = '/'.join([
                FILE_CONTENT_TYPE,
                FILE_MSWORD_EXTENSION
            ])  # application/msword
        elif attachment_extension_name in (FILE_PDF_TYPE, FILE_CSV_TYPE):   
            reformatted_attachment_type = attachment_content_type
    elif attachment_base_type == IMAGE_MESSAGE:
        reformatted_attachment_type = IMAGE_MESSAGE # image
    return reformatted_attachment_type


def format_atachment_type_from_zalo_message(attachment: Any, optionals: Any, index: int) -> str:
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

    return reformatted_attachment_type, attachment_name, attachment_size, attachment_id
