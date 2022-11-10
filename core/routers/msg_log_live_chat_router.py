from .base import BaseRouter
from core.schema import NatsChatMessage
from core.abstractions import AbsAppContext
from core import constants
from sop_chat_service.app_connect.models import Room
from core.utils import format_log_message


class MessageLogLiveChatRouter(BaseRouter):
    msg_type = constants.MESSAGE_LEAVE_LIVECHAT_LOG

    def bind_context(self, context: AbsAppContext, **kwargs):
        self.context = context

    async def process_message(self, data: NatsChatMessage, *args, **kwargs):
        room =  Room.objects.filter(room_id=data.room_id).first()
        if not room:
            return
        log_message = format_log_message(room, f'{constants.LOG_LEAVE_LIVECHAT}', constants.TRIGGER_LEFT_LEAVE_LIVECHAT)
        await self.context.run_send_message_manager(manager_type=constants.MESSAGE_LOG_MANAGER, message=log_message)
