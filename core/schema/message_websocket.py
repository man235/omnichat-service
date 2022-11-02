# -*- coding: utf-8 -*-
from typing import List, Optional, Dict
from .base_model import CustomBaseModel
# from .message_receive import NatsChatMessageAttachment


class ChatMessageAttachment(CustomBaseModel):
    name:Optional[str]
    type: Optional[str]
    url: Optional[str]
    size:Optional[str]

class ChatMessageUserInfo(CustomBaseModel):
    title: Optional[str]
    value: Optional[str]

class MessageChat(CustomBaseModel):
    mid: Optional[str]
    room_id: Optional[str]
    attachments: List[ChatMessageAttachment] = []
    user_info: List[ChatMessageUserInfo] = []
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
    user_id: Optional[str]
    timestamp: Optional[float]


class MessageToWebSocket(CustomBaseModel):
    mid: Optional[str]
    room_id: Optional[str]
    attachments: List[ChatMessageAttachment] = []
    user_info: List[ChatMessageUserInfo] = []
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
    user_id: List[str] = []
    timestamp: Optional[float]
