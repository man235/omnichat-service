# -*- coding: utf-8 -*-
from typing import List, Optional, Dict
from .base_model import CustomBaseModel


class NatsChatMessageAttachment(CustomBaseModel):
    name:Optional[str]
    type: Optional[str]
    payloadUrl: Optional[str]
    size: Optional[str]

class NatsChatMessageUserInfo(CustomBaseModel):
    title: Optional[str]
    value: Optional[str]
class ChatOptional(CustomBaseModel):
    chat_type: str
    data: Optional[Dict] = {}

class NatsChatMessage(CustomBaseModel):
    senderId: str
    recipientId: str
    timestamp: int
    text: Optional[str]
    mid: str
    appId: str
    attachments: List[NatsChatMessageAttachment] = []
    user_info: List[NatsChatMessageUserInfo] = []
    typeChat: str
    optionals: List[ChatOptional] = []
    uuid: Optional[str] = ""
    room_id: Optional[str] = None
