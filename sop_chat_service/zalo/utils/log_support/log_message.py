from sop_chat_service.app_connect.models import LogMessage, Message
from django.utils import timezone
from sop_chat_service.zalo.utils.log_support.log_constant import LOG_MESSAGES
from django.conf import settings
import asyncio
import nats
import uuid
import json

class LogMessageSupport:
    def __init__(self, log_messages: dict = None) -> None:
        if log_messages is None:
            self._log_messages = LOG_MESSAGES
        self._log_messages = log_messages
    
    @property
    def log_messages(self) -> dict:
        return self._log_messages
    
    @log_messages.setter
    def log_messages(self, log_messages: dict) -> None:
        self._log_messages = log_messages
    
    def get_message(self, trigger_type: str):
        log_message = self.log_messages().get(trigger_type)
        if not log_message:
            self._trigger_type = trigger_type
            
        return log_message

async def save_log_messages(
    room_id: str,
    msg: str,
    log_type: str,
    from_user: str = None,
    to_user: str = None,
) -> None:
    message = Message.objects.create(
        uuid=uuid.uuid4(),
        room_id=room_id,
        created_at=timezone.now(),
        timestamp=timezone.now().timestamp(),
        text=msg,
    )
    
    log_msg = LogMessage.objects.create(
        mid=message,
        log_type=log_type,
        from_user=from_user,
        to_user=to_user,
    )
    
    return log_msg

def format_log_message(log_message: LogMessage):    
    return {
        'log_type': log_message.log_type,
        'from_user': log_message.from_user,
        'to_user': log_message.to_user,
        'timestamp': log_message.mid.timestamp,
        'message': log_message.mid.text,
        'data': {
            'reminder': ...
        }
    }

async def connect_nats_client_publish_websocket(topic, data):
    nats_client = await nats.connect(settings.NATS_URL)
    await nats_client.publish(topic, bytes(data))
    await nats_client.close()
    return
