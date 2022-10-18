from core.schema.message_receive import NatsChatMessage
from sop_chat_service.app_connect.models import Message, Attachment, Room, ServiceSurvey
from sop_chat_service.live_chat.models import LiveChat




async def live_chat_save_message_store_database(room, data: NatsChatMessage):

    if room.type =="livechat":
        live_chat = LiveChat.objects.filter(id = data.recipientId).first()
        room = Room.objects.filter(room_id = room).first().update(user_id = live_chat.user_id)
        message = Message(
            room_id = room,
            fb_message_id = data.mid,
            sender_id = data.senderId,
            recipient_id = data.recipientId,
            text = data.text,
            uuid = data.uuid
        )
        message.save()
        if data.optionals[0].data.get("attachments"):
            for attachment in data.optionals[0].data.get('attachments'):
                Attachment.objects.create(
                    mid = message,
                    type = attachment['type'],
                    # attachment_id = attachment.id,
                    # url = attachment.url if attachment.url else attachment.video_url,
                    url = attachment['payloadUrl'],
                    # name = attachment.name,
                    # size = attachment.size
                )
                
        if data.optionals[0].data.get("user_info"):
            for item in data.optionals[0].data.get("user_info"):
                ServiceSurvey.objects.create(
                    mid = message,
                    name = item['title'],
                    value = item['value'],
                )

        return
    