from .base import BaseRouter
from core.schema import NatsChatMessage
from core.abstractions import AbsAppContext
from core import constants
from sop_chat_service.app_connect.models import Room
from core.utils import get_message_from_mid, facebook_format_mid_to_nats_message
from pydantic import parse_obj_as

class MessageTextRouter(BaseRouter):
    msg_type = constants.MESSAGE_TEXT

    def bind_context(self, context: AbsAppContext, **kwargs):
        self.context = context

    async def process_message(self, data: NatsChatMessage, *args, **kwargs):
        room: Room = await self.run_check_data_message(data)
        if not room:
            return
        if data.typeChat == constants.FACEBOOK:
            msg = get_message_from_mid(room.page_id.access_token_page, data.mid)
            fb_msg = facebook_format_mid_to_nats_message(room, msg, data)
            data = parse_obj_as(NatsChatMessage, fb_msg)
        await self.context.run_manager(manager_type=constants.WEBSOCKET_MANAGER, room=room, data=data)
        await self.context.run_manager(manager_type=constants.STORAGE_MANAGER, room=room, data=data)
