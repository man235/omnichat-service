from typing import Any, Optional
from core import constants
from core.constants.log_messages import MESSAGE_TYPE_LOG
from sop_chat_service.app_connect.models import LogMessage, Message, Room
from django.utils import timezone
from django.conf import settings
import logging
import uuid
import nats
import asyncio
import json

logger = logging.getLogger(__name__)


class LogMessageSupport:
    message_type: str = MESSAGE_TYPE_LOG
    
    def __init__(
        self,
        trigger: Optional[str] = None,
        message: Optional[str] = None,
        **kwargs: Optional[str]
    ) -> None:
        self._trigger = trigger
        self._message = message
    
    @property
    def trigger(self) -> str:
        return self._trigger
    
    @trigger.setter
    def trigger(self, trigger: str) -> None:
        self._trigger = trigger
        
    @property
    def message(self) -> str:
        return self.message
    
    @message.setter
    def message(self, message: str) -> None:
        self._message = message
        
    def save(
        self,
        room: Room,
        **user_id: Optional[str],
    ) -> LogMessage:
        message = Message.objects.create(
            uuid=uuid.uuid4(),
            room_id=room,
            created_at=timezone.now(),
            timestamp=timezone.now().timestamp(),
        )

        _formatted_message = str(self._message).format(
            from_user=user_id.get('from_user', None),
            to_user=user_id.get('to_user', None)
        )
        log_message_model = LogMessage.objects.create(
            mid=message,
            room_id=room.room_id,
            log_type=self._trigger,
            message=_formatted_message,
            from_user=user_id.get('from_user', None),
            to_user=user_id.get('to_user', None),
            created_at=timezone.now(),
        )
                
        return log_message_model
    
def format_log_message(
    log_message: LogMessage = None,
    **optional_data: Optional[Any]
) -> dict:
    if not isinstance(log_message, LogMessage):
        raise ValueError('log_message must be a LogMessage model')
        
    return {
        'message_type': LogMessageSupport.message_type,
        'data': {
            'log_type': log_message.log_type,
            'message': log_message.message,
            'from': log_message.from_user,
            'to': log_message.to_user,
            'created_at': log_message.created_at,
            'optional': optional_data
        }
    }

async def connect_nats_client_publish_websocket(topic: str, message: str):
    nats_client = await nats.connect(settings.NATS_URL)
    await nats_client.publish(topic, bytes(message))
    await nats_client.close()
    return
    
async def pub_log_message_to_nats(
    room_id: str,
    formatted_message: dict,
    topic: Optional[str] = None,
) -> None:
    topic = f'{constants.CHAT_SERVICE_TO_CORECHAT_PUBLISH}.{room_id}'

    logger.debug(f'{function.__name__} ********************************************************************* ')
    
    asyncio.run(
        connect_nats_client_publish_websocket(
            topic,
            json.dumps(formatted_message).encode()
        )
    )
