import time
from sop_chat_service.app_connect.models import Attachment, Room
from sop_chat_service.app_connect.serializers.message_serializers import MessageSerializer
from django.utils import timezone
from sop_chat_service.live_chat.models import LiveChat


def format_message(data):
    sz = MessageSerializer(data,many=False)
    attachments = []
    data_attachment = sz.data.get('attachments')
    if data_attachment:
        file = Attachment.objects.filter(id in data_attachment)
        for item in file:
            attachment = {
                "id": file.id,
                "type": file.type,
                "name": file.name,
                "url":file.url,
                "size": "",
                "video_url": ""
      
            }
            attachments.append(attachment)
    room= Room.objects.filter(room_message__id =sz.data['id']).first()
    live_chat = LiveChat.objects.filter(user_id = sz.data['sender_id']).first()
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
        "live_chat_id":live_chat.id,
    }
    return data_mid_json