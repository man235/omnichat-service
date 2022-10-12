# -*- coding: utf-8 -*-
from typing import List, Optional, Dict
from .base_model import CustomBaseModel
# from .message_receive import NatsChatMessageAttachment


class ChatMessageAttachment(CustomBaseModel):
    type: Optional[str]
    url: Optional[str]

class MessageWebSocket(CustomBaseModel):
    mid: Optional[str]
    room_id: Optional[str]
    attachments: List[ChatMessageAttachment] = []
    created_at: str
    is_seen: Optional[str]
    is_sender: bool = False
    message_reply: Optional[str]
    reaction: Optional[str] = None
    recipient_id: str
    reply_id: Optional[str] = None
    sender_id: str
    sender_name: Optional[str] = None
    text: Optional[str] = None
    uuid: Optional[str]
    created_time: Optional[str]
    event: Optional[str]
