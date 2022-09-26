from django.utils import timezone
import json


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
        # for attachment in data_attachment:
        attachment = {
            "id": attachment_data[0]['id'],
            "type": attachment_data[0]['mime_type'],
            "name": attachment_data[0]['name'],
            "url": data_msg.get('attachments')[0]['payloadUrl'] if data_msg.get('attachments') else None,
            "size": attachment_data[0].get('size'),
            "video_url": attachment_data[0]['video_data']['url'] if attachment_data[0].get('video_data') else None
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
            "size": data_attachment.get('data')[0]['size']
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
        "uuid": str(uuid)
    }
    return data_mid_json
