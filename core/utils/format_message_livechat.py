import time
from sop_chat_service.app_connect.models import Attachment, Room
from sop_chat_service.app_connect.serializers.message_serializers import MessageSerializer
from django.utils import timezone
# from sop_chat_service.live_chat.models import LiveChat
from core.schema import NatsChatMessage, NatsChatMessageAttachment, NatsChatMessageUserInfo
from core import constants


def format_message(data):
    sz = MessageSerializer(data,many=False)
    attachments = []
    data_attachment = sz.data.get('attachments')
    if data_attachment:
        for attachment in data_attachment:
            file = Attachment.objects.filter(id = attachment.get("id")).first()
            attachment_dt = {
                "id": file.id,
                "type": file.type,
                "name": file.name,
                "url":file.url,
                "size": "",
                "video_url": ""
      
            }
            attachments.append(attachment_dt)
    room= Room.objects.filter(room_message__id =sz.data['id']).first()
    # live_chat = LiveChat.objects.filter(user_id = sz.data['sender_id']).first()
    data_mid_json = {
        "mid": sz.data['id'],
        "attachments": attachments,
        "text": sz.data['text'],
        "sender_id": sz.data['sender_id'],
        "recipient_id":  sz.data['recipient_id'],
        "room_id": room.room_id,
        "is_sender": True,
        "created_at": str(timezone.now()),
        "is_seen": None,
        "message_reply": None,
        "reaction": None,
        "reply_id": None,
        "sender_name": None,
        "uuid": sz.data['uuid'],
        "timestamp":int(time.time()),
        "typeChat":"livechat",
        "appId":"",
        # "live_chat_id":live_chat.id,
        "event": "live_chat_new_message",
    }
    return data_mid_json


def format_message_to_nats_chat_message(room, data):
    sz = MessageSerializer(data,many=False)
    attachments = []
    data_attachment = sz.data.get('attachments')
    if data_attachment:
        for attachment in data_attachment:
            file = Attachment.objects.filter(id = attachment.get("id")).first()
            message_att = NatsChatMessageAttachment(
                name = file.name,
                type = file.type,
                payloadUrl = file.url,
                size = file.size
            )
            attachments.append(message_att)
    message_user_info = NatsChatMessageUserInfo(
        title = None,
        value = None
    )
    message_mid = NatsChatMessage(
        senderId = sz.data['sender_id'],
        recipientId = sz.data['recipient_id'],
        timestamp = int(time.time()),
        text = sz.data['text'],
        mid = sz.data['id'],
        appId = "",
        attachments = attachments,
        user_info = [],
        typeChat = constants.LIVECHAT,
        optionals = [],
        uuid = sz.data['uuid'],
        room_id = room.room_id
    )
    return message_mid
