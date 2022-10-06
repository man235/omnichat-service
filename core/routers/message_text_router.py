from .base import BaseRouter
from core.schema import CoreChatInputMessage
from core.abstractions import AbsAppContext
from core import constants
from typing import Dict
from core.utils import format_message_data_for_websocket
from sop_chat_service.app_connect.models import Room


class MessageTextRouter(BaseRouter):
    msg_type = constants.MESSAGE_TEXT

    def bind_context(self, context: AbsAppContext, **kwargs):
        self.context = context

    async def process_message(self, message: CoreChatInputMessage, data: Dict, *args, **kwargs):
        room: Room = await self.run_check_data_message(message, data)
        if not room:
            return
        data_format = format_message_data_for_websocket(data, data['_uuid'])
        await self.context.run_manager(manager_type=constants.WEBSOCKET_MANAGER, room=room, data=data_format, message=message)
        await self.context.run_manager(manager_type=constants.STORAGE_MANAGER, room=room, data=data, message=message)
