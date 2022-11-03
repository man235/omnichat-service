import asyncio
import json
from typing import Any, Optional
from core import constants
from sop_chat_service.app_connect.models import LogMessage, Message
from django.utils import timezone
from django.conf import settings
import uuid
import nats


class LogMessageSupport:
    def __init__(self, trigger: str, **kwargs: Optional[str]) -> None:
        self._trigger = trigger
    
    @property
    def trigger(self) -> dict:
        return self._trigger
    
    @trigger.setter
    def trigger(self, trigger: str) -> None:
        self._trigger = trigger
        
    def save_log(
        self,
        room_id: str,
        **user_id: Optional[str],
    ) -> LogMessage:
        message = Message.objects.create(
            uuid=uuid.uuid4(),
            room_id=room_id,
            created_at=timezone.now(),
            timestamp=timezone.now().timestamp(),
        )
        log_msg = LogMessage.objects.create(
            mid=message,
            log_type=self._trigger_type,
            from_user=user_id.get('from_user'),
            to_user=user_id.get('to_user'),
        )
        return log_msg
    
    def format_log_message_for_socket(log_message: LogMessage, **optional_data: Optional[Any]) -> dict:    
        return {
            'log_type': log_message.log_type,
            'from': log_message.from_user,
            'to': log_message.to_user,
            'created_at': log_message.mid.created_at,
            'data': optional_data,
        }

async def pub_nats_and_emit_socket(
    formatted_message: dict,
    room_id: str,
    topic: Optional[str]
) -> None:
    async def connect_nats_client_publish_websocket(topic: str, message: str):
        topic = f'{constants.CHAT_SERVICE_TO_CORECHAT_PUBLISH}.{room_id}'
        nats_client = await nats.connect(settings.NATS_URL)
        await nats_client.publish(topic, bytes(formatted_message))
        await nats_client.close()
        return
        
    asyncio.run(
        connect_nats_client_publish_websocket(
            topic,
            json.dumps(formatted_message).encode()
        )
    )