from .base import BaseRouter
from core.schema import FormatSendMessage
from core.abstractions import AbsAppContext
from core import constants


class MessageLogRouter(BaseRouter):
    msg_type = constants.MESSAGE_LOG

    def bind_context(self, context: AbsAppContext, **kwargs):
        self.context = context

    async def process_message(self, message: FormatSendMessage, *args, **kwargs):
        await self.context.run_send_message_manager(manager_type=constants.MESSAGE_LOG_MANAGER, message=message)
