from core.abstractions import AbsCheckDataMessage

class BaseCheckDataMessageManager(AbsCheckDataMessage):
    chat_type: str = None

    async def check_data_message(self, *args, **kwargs):
        print("BaseCheckDataMessageManager handle_message: ---------------------- ")
        pass
