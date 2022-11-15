# -*- coding: utf-8 -*-
from pydantic import BaseModel
from typing import List, Optional, Dict
from .base_model import CustomBaseModel
from core import constants


class CoreChatInputMessage(BaseModel):
    msg_type: str
    chat_type: str


class SendMessageAttachment(CustomBaseModel):
    id: Optional[str]
    type: Optional[str]
    url: Optional[str]
    name: Optional[str]
    size: Optional[str]
    video_url: Optional[str]

class LogMessageSchema(CustomBaseModel):
    log_type:Optional[str]
    message: Optional[str]
    room_id: Optional[str]
    from_user: Optional[str]
    to_user: Optional[str]
    created_at: Optional[str]

class FormatSendMessage(CustomBaseModel):
    mid: Optional[str]
    attachments: List[SendMessageAttachment] = []
    text: Optional[str] = None
    created_time: Optional[str]
    sender_id: str
    recipient_id: str
    room_id: Optional[str]
    is_sender: bool = False
    created_at: str
    is_seen: Optional[str]
    message_reply: Optional[str]
    reaction: Optional[str] = None
    reply_id: Optional[str] = None
    sender_name: Optional[str] = None
    uuid: Optional[str]
    msg_status: Optional[str] = constants.SEND_MESSAGE_STATUS
    type : Optional[str] = constants.FACEBOOK
    user_id: List[str] = []
    event: Optional[str]
    is_log_msg: Optional[bool] = False
    log_message: Optional[LogMessageSchema] = None

class UpdateRoom(CustomBaseModel):
    room_id: str
    status: Optional[str]
    event: Optional[str] = constants.UPDATE_STATUS_ROOM