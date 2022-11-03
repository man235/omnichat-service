from typing import Any, Optional
from core import constants
from core.constants.log_triggers import LOG_MESSAGE_TYPE
from sop_chat_service.app_connect.models import LogMessage, Message
from django.utils import timezone
from django.conf import settings
import logging
import uuid
import nats
import asyncio
import json

logger = logging.getLogger(__name__)


class LogMessageSupport:
    _message_type: str = LOG_MESSAGE_TYPE
    
    def __init__(
        self,
        trigger: Optional[str] = None,
        **kwargs: Optional[str]
    ) -> None:
        self._trigger = trigger
    
    @property
    def trigger(self) -> dict:
        return self._trigger
    
    @trigger.setter
    def trigger(self, trigger: str) -> None:
        self._trigger = trigger
        
    def save(
        self,
        room_id: str,
        **user_id: Optional[str],
    ) -> LogMessage:
        message = Message.objects.create(
            uuid=uuid.uuid4(),
            created_at=timezone.now(),
            timestamp=timezone.now().timestamp(),
        )
        log_message = LogMessage.objects.create(
            mid=message,
            room_id=room_id,
            log_type=self._trigger_type,
            from_user=user_id.get('from_user', None),
            to_user=user_id.get('to_user', None),
        )
        
        # add or update instance attributes
        self._log_message = log_message
        
        return log_message
    
    @classmethod
    def format_data(
            self,
            log_message: Optional[LogMessage] = None,
            **optional_data: Optional[Any]
        ) -> dict:    
        if log_message is None:
            if hasattr(self, '_log_message'):
                log_message = self._log_messages
            else:
                raise ValueError(f'log_message is None. Call "save_log" function before')
        elif not isinstance(log_message, LogMessage):
            raise ValueError('log_message must be a LogMessage model')
        
        return {
            'message_type': self._message_type,
            'log_type': log_message.log_type,
            'from': log_message.from_user,
            'to': log_message.to_user,
            'created_at': log_message.mid.created_at,
            'data': optional_data,
        }


async def pub_nats_and_emit_socket_log_msg(
    room_id: str,
    formatted_message: dict,
    topic: Optional[str] = None,
) -> None:
    async def connect_nats_client_publish_websocket(topic: str, message: str):
        topic = f'{constants.CHAT_SERVICE_TO_CORECHAT_PUBLISH}.{room_id}' if not topic else topic
        nats_client = await nats.connect(settings.NATS_URL)
        await nats_client.publish(topic, bytes(message))
        await nats_client.close()
        return
    
    logger.debug(f'{function.__name__} ********************************************************************* ')
    
    asyncio.run(
        connect_nats_client_publish_websocket(
            topic,
            json.dumps(formatted_message).encode()
        )
    )
