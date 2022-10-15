from django.utils import timezone
import json
from core.schema import NatsChatMessage, MessageWebSocket, ChatMessageAttachment
from core.schema.message_websocket import ChatMessageUserInfo
from core import constants


def format_receive_message(data: NatsChatMessage):
    attachments = [ChatMessageAttachment(url=attachment.payloadUrl, type=attachment.type) for attachment in data.attachments]
    message_ws = MessageWebSocket(
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
        room_id = None,
        created_time = None
    )
    return message_ws

def format_message_from_corechat_to_websocket(room ,data: NatsChatMessage):
    attachments = [ChatMessageAttachment(url=attachment.payloadUrl, type=attachment.type) for attachment in data.attachments]
    user_info = [ChatMessageUserInfo(title=user_info.title, value=user_info.value) for user_info in data.user_info]
    message_ws = MessageWebSocket(
        attachments = attachments,
        user_info = user_info,
        created_at = str(timezone.now()),
        is_seen = "",
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
        event= "live_chat_new_message",
    )
    return message_ws


def format_message_from_corechat_to_webhook(room ,data: NatsChatMessage):
    attachments = [ChatMessageAttachment(url=attachment.payloadUrl, type=attachment.type) for attachment in data.attachments]
    message_ws = MessageWebSocket(
        attachments = attachments,
        created_at = str(timezone.now()),
        is_seen = "",
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
        event= "live_chat_new_message_ack",
    )
    return message_ws

def format_mid_facebook(room, message_response):
    attachments = []
    data_attachment = message_response.get('attachments')
    if data_attachment:
        attachment_data =data_attachment.get('data')
        for attachment in attachment_data:
            dt_attachment = {
                "id": attachment['id'],
                "type": attachment['mime_type'],
                "name": attachment['name'],
                # "url": attachment['image_data']['url'] if attachment.get('image_data') else None,
                "url": attachment.get('image_data')['url'] if attachment.get('image_data') else attachment.get('file_url'),
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


def format_message_data_for_websocket(data, uuid):
    data = {
        "attachments": data.get("attachments"),
        "created_at": str(timezone.now()),
        "is_seen": None,
        "is_sender": True if data.get("is_sender") == True else False,
        "message_reply": None,
        "reaction": None,
        "recipient_id": data.get("recipient_id"),
        "reply_id": None,
        "sender_id": data.get("senderId"),
        "sender_name": None,
        "text": data.get("text"),
        "uuid": str(uuid)
    }
    data_res = json.dumps(data)
    return data_res


def format_data_from_facebook_nats_subscribe(room, message_response, data_msg):
    attachments = []
    data_attachment = message_response.get('attachments')
    if data_attachment:
        attachment_data =data_attachment.get('data')
        for attachment in attachment_data:
            dt_attachment = {
                "id": attachment['id'],
                "type": attachment['mime_type'],
                "name": attachment['name'],
                # "url": attachment['image_data']['url'] if attachment.get('image_data') else None,
                "url": attachment.get('image_data')['url'] if attachment.get('image_data') else attachment.get('file_url'),
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


def format_data_from_facebook(room, message_response, uuid):
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
        "room_id": room.id,
        "is_sender": True,
        "created_at": str(timezone.now()),
        "is_seen": None,
        "message_reply": None,
        "reaction": None,
        "reply_id": None,
        "sender_name": None,
        "uuid": str(uuid),
        "msg_status": constants.SEND_MESSAGE_STATUS
    }
    return data_mid_json
