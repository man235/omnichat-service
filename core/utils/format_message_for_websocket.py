from django.utils import timezone
import json


def format_message_data_for_websocket(data):
    data = {
        "attachments": data.get("attachments"),
        "created_at": timezone.now(),
        "is_seen": None,
        "is_sender": False,
        "message_reply": None,
        "reaction": None,
        "recipient_id": data.get("recipientId"),
        "reply_id": None,
        "sender_id": data.get("senderId"),
        "sender_name": None,
        "text": data.get("text")
    }
    data_res = json.dumps(data)
    return data_res
