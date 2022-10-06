from pydantic import BaseModel


class CoreChatInputMessage(BaseModel):
    msg_type: str
    chat_type: str
