from .base import BaseRouter
from core.schema import NatsChatMessage
from core.abstractions import AbsAppContext
from core import constants


class ActionFollowRouter(BaseRouter):
    msg_type = constants.ACTION_FOLLOW

    def bind_context(self, context: AbsAppContext, **kwargs):
        self.context = context

    async def process_message(self, data: NatsChatMessage, *args, **kwargs):
        await self.context.run_manager(manager_type=constants.ACTION_FOLLOW_MANAGER, room=None, data=data)
