from typing import Dict
from core.schema import NatsChatMessage
from core.check_data_message import CheckDataMessageFacebook, CheckDataMessageLiveChat, CheckDataMessageZalo
from core.abstractions import AbsRouter, SingletonClass, AbsAppContext, AbsCheckDataMessage


class BaseRouter(SingletonClass, AbsRouter):
    msg_type: str = None
    _check_data_message: Dict[str, AbsCheckDataMessage] = {}

    def _singleton_init(self, **kwargs):
        self._initialized: bool = False

    def bind_context(self, context: AbsAppContext, **kwargs):
        self.context = context

    async def process_message(self, *args, **kwargs):
        pass

# ----------------    CHECK DATA MESSAGE    ----------------
    async def _get_check_data_message(self, chat_type: str) -> Dict[str, AbsCheckDataMessage]:
        for router_class in (CheckDataMessageFacebook, CheckDataMessageLiveChat, CheckDataMessageZalo):
            router_instance = router_class()
            self._check_data_message.update({router_instance.chat_type: router_instance})
        return self._check_data_message.get(chat_type)

    async def run_check_data_message(self, data: NatsChatMessage, **kwargs):
        check_data_message: AbsCheckDataMessage = await self._get_check_data_message(data.typeChat)
        if check_data_message:
            # Check Fanpage - User_app - Room --> Room
            room = await check_data_message.check_data_message(data)
            return room
        else:
            print(f'not found router for {data.typeMessage}')
# ----------------    END CHECK DATA MESSAGE    ----------------
