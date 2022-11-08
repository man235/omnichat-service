from core.schema import FormatSendMessage, LogMessageSchema
from django.utils import timezone
from sop_chat_service.app_connect.models import Room, Message, LogMessage
import uuid
from core import constants

def format_log_message(room: Room, message_log: str, type_log: str):
    _time_now = str(timezone.now())
    log_message = LogMessageSchema(
        log_type = type_log,
        message = message_log,
        room_id = room.room_id,
        from_user = room.page_id.page_id,
        to_user = room.external_id,
        created_at = _time_now,
    )

    log_message = FormatSendMessage(
        mid = None,
        attachments = [],
        text = message_log,
        created_time = _time_now,
        sender_id = room.page_id.page_id if room.page_id else room.user_id,
        recipient_id = room.external_id,
        room_id = room.room_id,
        is_sender = True,
        created_at = _time_now,
        is_seen = True,
        message_reply = None,
        reaction = None,
        reply_id = None,
        sender_name = None,
        uuid = str(uuid.uuid4()),
        msg_status = constants.MESSAGE_LOG,
        type  = room.type,
        user_id = [room.user_id, room.admin_room_id] if room.admin_room_id else [room.user_id],
        event = None,
        is_log_msg = True,
        log_message = log_message
    )
    return log_message.dict()


async def storage_log_message(room: Room, message_log: FormatSendMessage):
    message = Message(
        room_id = room,
        fb_message_id = message_log.mid,
        sender_id = message_log.sender_id,
        recipient_id = message_log.recipient_id,
        text = message_log.text,
        is_sender= True,
        is_seen = timezone.now(),
        uuid = message_log.uuid
    )
    message.save()
    LogMessage.objects.create(
        mid = message,
        log_type = message_log.log_message.log_type,
        message = message_log.text,
        room_id = message_log.room_id,
        from_user = room.page_id.page_id,
        to_user = room.external_id
    )
    return
