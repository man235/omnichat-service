from core.schema.message_receive import ChatOptional
from sop_chat_service.app_connect.models import Message, Attachment, Room
from django.utils import timezone
from core.schema import MessageWebSocket
from django.conf import settings
import uuid

from sop_chat_service.zalo.utils.api_suport.api_zalo_caller import get_message_data_of_zalo_user
from sop_chat_service.zalo.utils.chat_support.upload_file_to_minio import upload_file_to_minio_zalo


async def save_message_store_database_zalo(
    room,
    msg: MessageWebSocket,
    optionals: list[ChatOptional] = None
) -> None:
    # data_res = get_message_from_mid(room.page_id.access_token_page, data_msg.get("mid"))
    # data = format_data_from_facebook_nats_subscribe(room, data_res, data_msg)
    message = Message(
        room_id = room,
        fb_message_id = msg.mid,
        sender_id = msg.sender_id,
        recipient_id = msg.recipient_id,
        text = msg.text,
        sender_name = room.name,
        uuid = msg.uuid,
    )
    message.save()
    if msg.attachments:
        for index, attachment in enumerate(msg.attachments):
            domain = settings.DOMAIN_MINIO_SAVE_ATTACHMENT
            sub_url = f"api/live_chat/chat_media/get_chat_media?name=live_chat_room_{room.room_id}/"
            print(f'url +++++++++++++++++++++++++++++++++')
            url = ''.join([domain, sub_url])
            print(f'url +++++++++++++++++++++++++++++++++ {url}')
            data_upload_file = upload_file_to_minio_zalo(attachment, room.room_id)
            print(f'store_sending_message_zalo ---------- data_upload_file-{data_upload_file}')  
            
            # if not optionals[index] and not optionals[index].data.get('attachments'):
            #     attachment_payload_name = None
            #     attachment_payload_size = None
            #     attachment_payload_type = None
            #     pass
            # else:
            #     optional_attachment_payload = optionals[index].data.get('attachments')[index].get('payload')
            #     attachment_payload_name = optional_attachment_payload.get('name')
            #     attachment_payload_size = optional_attachment_payload.get('size')
            #     attachment_payload_type = optional_attachment_payload.get('type')
            
            Attachment.objects.create(
                mid = message,
                type = '/'.join([attachment.type, 'somethingelse']),
                # attachment_id = optional_attachment_payload.get('id'),
                url = ''.join([url, data_upload_file]),
                # name = attachment_payload_name,
                # size = attachment_payload_size
            )

def fetch_attachment_url_zalo(
    
) -> None:
    pass


def store_sending_message_in_database(
    room: Room,
    mid: str,
    sender_id: str, 
    recipient_id: str,
    text: str,
    attachments: list[dict] = None,
    is_sender: bool = True,
    is_seen = timezone.now(), 
    uuid: str = uuid.uuid4(),
) -> None:
    
    message = Message(
        room_id = room,
        fb_message_id = mid,
        sender_id = sender_id,
        recipient_id = recipient_id,
        text = text,
        is_sender= is_sender,
        is_seen = is_seen,
        uuid = uuid
    )
    message.save()
    
    if attachments:
        attachments = attachments
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
            