from django.utils import timezone
import json
from typing import Dict

import time
from core.schema import NatsChatMessage, MessageChat, ChatMessageAttachment, MessageToWebSocket
from core.schema.message_websocket import ChatMessageUserInfo
from core import constants
from sop_chat_service.app_connect.models import Room


def format_receive_message_zalo(room, data: NatsChatMessage):
    list_msg = []
    attachments = [ChatMessageAttachment(url=attachment.payloadUrl, type=attachment.type, name=attachment.name, size=attachment.size) for attachment in data.attachments]
    for _room in room:
        message_ws = MessageChat(
            attachments = attachments,
            # attachments = data.attachments,
            created_at = str(timezone.now()),
            is_seen = False,
            is_sender = False,
            message_reply = None,
            reaction = None,
            recipient_id = data.recipientId,
            reply_id = None,
            sender_id = data.senderId,
            sender_name = None,
            text = data.text,
            uuid = data.uuid,
            mid = data.mid,
            room_id = _room.room_id,
            created_time = None,
            user_id = _room.user_id,
            event = constants.SIO_EVENT_NEW_MSG_CUSTOMER_TO_SALEMAN
        )
        list_msg.append(message_ws)
    return list_msg


def format_receive_message(room, data: NatsChatMessage):
    attachments = [ChatMessageAttachment(url=attachment.payloadUrl, type=attachment.type, name=attachment.name, size=attachment.size) for attachment in data.attachments]
    message_ws = MessageChat(
        attachments = attachments,
        # attachments = data.attachments,
        created_at = str(timezone.now()),
        is_seen = False,
        is_sender = False,
        message_reply = None,
        reaction = None,
        recipient_id = data.recipientId,
        reply_id = None,
        sender_id = data.senderId,
        sender_name = None,
        text = data.text,
        uuid = data.uuid,
        mid = data.mid,
        room_id = room.room_id,
        created_time = None,
        user_id = room.user_id,
        timestamp = data.timestamp,
        event = constants.SIO_EVENT_NEW_MSG_CUSTOMER_TO_SALEMAN
    )
    return message_ws

def livechat_format_message_from_corechat_to_websocket(room ,data: NatsChatMessage, event: str, is_sender: bool):
    user_id = []
    if room.admin_room_id:
        user_id = [room.admin_room_id, room.user_id]
    else:
        user_id = [room.user_id]
    attachments= []
    user_info=[]
    attachments = [ChatMessageAttachment(url=attachment.payloadUrl, type=attachment.type,name=attachment.name,size=attachment.size) for attachment in data.attachments]
    if data.optionals:
        if data.optionals[0].data.get("user_info"):
            user_info = [ChatMessageUserInfo(title=user_info['title'], value=user_info['value']) for user_info in data.optionals[0].data.get("user_info")]
        if data.optionals[0].data.get("is_sender"):
            is_sender = data.optionals[0].data.get("is_sender")
    message_ws = MessageToWebSocket(
        attachments = attachments,
        user_info = user_info,
        created_at = str(timezone.now()),
        is_seen = "",
        is_sender =  is_sender,
        message_reply = None,
        reaction = None,
        recipient_id = data.recipientId,
        reply_id = None,
        sender_id = data.senderId,
        sender_name = None,
        text = data.text,
        uuid = data.uuid,
        mid = data.mid,
        room_id = room.room_id,
        event = event,
        user_id = user_id,
        timestamp = data.timestamp
    )
    return message_ws


def livechat_format_message_from_corechat_to_webhook(room ,data: NatsChatMessage, event: str, is_sender: bool):
    user_id = []
    if room.admin_room_id:
        user_id = [room.admin_room_id, room.user_id]
    else:
        user_id = [room.user_id]
    attachments= []
    user_info=[]
    attachments = [ChatMessageAttachment(url=attachment.payloadUrl, type=attachment.type,name=attachment.name,size=attachment.size) for attachment in data.attachments]
    if data.optionals:
        if data.optionals[0].data.get("is_sender"):
            is_sender = data.optionals[0].data.get("is_sender")
        if data.optionals[0].data.get("user_info"):
            user_info = [ChatMessageUserInfo(title=user_info['title'], value=user_info['value']) for user_info in data.optionals[0].data.get("user_info")]
    message_ws = MessageToWebSocket(
        attachments = attachments,
        user_info = user_info,
        created_at = str(timezone.now()),
        is_seen = "",
        is_sender = is_sender,
        message_reply = None,
        reaction = None,
        recipient_id = data.recipientId,
        reply_id = None,
        sender_id = data.senderId,
        sender_name = None,
        text = data.text,
        uuid = data.uuid,
        mid = data.mid,
        room_id = room.room_id,
        user_id = user_id,
        event = event,
        timestamp = data.timestamp
    )
    return message_ws

def facebook_format_mid(room, message_response):
    attachments = []
    data_attachment = message_response.get('attachments')
    if data_attachment:
        attachment_data =data_attachment.get('data')
        for attachment in attachment_data:
            att = attachment.get('image_data')['url'] if attachment.get('image_data') else attachment.get('file_url')
            dt_attachment = {
                "id": attachment['id'],
                "type": attachment['mime_type'],
                "name": attachment['name'],
                # "url": attachment['image_data']['url'] if attachment.get('image_data') else None,
                "url": att if att else attachment.get('video_data').get('url'),
                "payloadUrl": att if att else attachment.get('video_data').get('url'),
                "size": attachment.get('size'),
                "video_url": attachment['video_data']['url'] if attachment.get('video_data') else None
            }
            attachments.append(dt_attachment)
    data_mid_json = {
        "mid": message_response['id'],
        "attachments": attachments,
        "text": message_response['message'],
        "created_time": message_response['created_time'],
        "sender_id": message_response['from']['id'],
        "recipient_id": message_response['to']['data'][0]['id'],
        "room_id": room.id,
        "is_sender": True,
        "created_at": str(timezone.now()),
        "is_seen": None,
        "message_reply": None,
        "reaction": None,
        "reply_id": None,
        "sender_name": None
    }
    return data_mid_json


def facebook_format_mid_to_nats_message(room, message_response, data: NatsChatMessage):
    attachments = []
    data_attachment = message_response.get('attachments')
    if data_attachment:
        attachment_data =data_attachment.get('data')
        for attachment in attachment_data:
            att = attachment.get('image_data')['url'] if attachment.get('image_data') else attachment.get('file_url')
            dt_attachment = {
                "id": attachment['id'],
                "type": attachment['mime_type'],
                "name": attachment['name'],
                # "url": attachment['image_data']['url'] if attachment.get('image_data') else None,
                "url": att if att else attachment.get('video_data').get('url'),
                "payloadUrl": att if att else attachment.get('video_data').get('url'),
                "size": attachment.get('size'),
                "video_url": attachment['video_data']['url'] if attachment.get('video_data') else None
            }
            attachments.append(dt_attachment)
    data_mid_json = {
        "mid": message_response['id'],
        "attachments": attachments,
        "text": message_response['message'],
        "created_time": message_response['created_time'],
        "senderId": message_response['from']['id'],
        "recipientId": message_response['to']['data'][0]['id'],
        "room_id": room.id,
        "is_sender": True,
        "created_at": str(timezone.now()),
        "is_seen": None,
        "message_reply": None,
        "reaction": None,
        "reply_id": None,
        "sender_name": None,
        "timestamp": data.timestamp,
        "appId": message_response['from']['id'],
        "typeChat": constants.FACEBOOK,
        "uuid": data.uuid,
        "typeMessage": data.typeMessage
    }
    return data_mid_json


def facebook_format_data_from_mid_facebook(room, message_response, uuid):
    attachments = []
    data_attachment = message_response.get('attachments')
    if data_attachment:
        # for attachment in data_attachment:
        attachment = {
            "id": data_attachment.get('data')[0]['id'],
            "type": data_attachment.get('data')[0]['mime_type'],
            "name": data_attachment.get('data')[0]['name'],
            "url": (
                data_attachment.get('data')[0]['image_data']['url'] if 
                data_attachment.get('data')[0].get('image_data') else
                data_attachment.get('data')[0].get('file_url')
            ),
            "size": data_attachment.get('data')[0]['size'],
            "video_url": data_attachment.get('data')[0]['video_data']['url'] if 
                data_attachment.get('data')[0].get('video_data') else None
        }
        attachments.append(attachment)
    data_mid_json = {
        "mid": message_response['id'],
        "attachments": attachments,
        "text": message_response['message'],
        "created_time": message_response['created_time'],
        "sender_id": message_response['from']['id'],
        "recipient_id": message_response['to']['data'][0]['id'],
        "room_id": room.room_id,
        "id": room.id,
        "is_sender": True,
        "created_at": str(timezone.now()),
        "is_seen": None,
        "message_reply": None,
        "reaction": None,
        "reply_id": None,
        "sender_name": None,
        "uuid": str(uuid),
        "msg_status": constants.SEND_MESSAGE_STATUS,
        "user_id": [room.user_id],
        "event": constants.SIO_EVENT_ACK_MSG_SALEMAN_TO_CUSTOMER
    }
    return data_mid_json

def format_receive_message_to_websocket(room, data: NatsChatMessage):
    user_id = []
    if room.admin_room_id:
        user_id = [room.admin_room_id, room.user_id]
    else:
        user_id = [room.user_id]
    attachments = [ChatMessageAttachment(url=attachment.payloadUrl, type=attachment.type, name=attachment.name, size=attachment.size) for attachment in data.attachments]
    message_ws = MessageToWebSocket(
        attachments = attachments,
        # attachments = data.attachments,
        created_at = str(timezone.now()),
        is_seen = False,
        is_sender = False,
        message_reply = None,
        reaction = None,
        recipient_id = data.recipientId,
        reply_id = None,
        sender_id = data.senderId,
        sender_name = None,
        text = data.text,
        uuid = data.uuid,
        mid = data.mid,
        room_id = room.room_id,
        created_time = None,
        user_id = user_id,
        timestamp = data.timestamp,
        event = constants.SIO_EVENT_NEW_MSG_CUSTOMER_TO_SALEMAN
    )
    return message_ws
def format_room(room:Dict):
    room= {
        "room_id":room.get('room_id'),
        "status":room.get('status'),
        "user_id": [room.get('user_id'), room.get('admin_room_id')] if room.get('admin_room_id') else [room.get('user_id')],
        "event" :constants.UPDATE_STATUS_ROOM,
    }
    return room
