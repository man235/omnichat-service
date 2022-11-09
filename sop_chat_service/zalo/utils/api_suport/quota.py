from email import message
from typing import Any
from django.conf import settings
import requests
import json
from sop_chat_service.app_connect.models import Message, Room

from sop_chat_service.zalo.utils.api_suport.response_templates import json_response


def get_last_message_from_zalo_user(
    room_queryset: Room,
) -> Message:
    if not room_queryset:
        raise ValueError('room_queryset must not be None')
    
    zalo_user_id = room_queryset.external_id
    
    return Message.objects.filter(
        is_sender=False,    # is message from Zalo
        sender_id=zalo_user_id,    # zalo user id
    ).last()

    
def get_zalo_command_quota(
    access_token: str = None,
    message_id: str = None
) -> Any:
    try:
        if message_id:  # reply message quota
            payloads = json.dumps({
                'message_id': message_id
            })
        else:   # active message quota
            payloads = None
                                
        rp = requests.post(
            url=f'{settings.ZALO_OA_OPEN_API}/quota/message',
            headers={
                'Content-Type': 'application/json',
                'access_token': access_token, 
            },
            data=payloads,
            timeout=15,
        )
        print(rp.status_code)
        if rp.status_code == 200:        
            if rp.json().get('message') ==  'Success':
                rp_json = rp.json()
                return json_response(True, rp_json.get('data'))
            else:
                return json_response(False, rp_json)
        else:
            return None
        
    except Exception as e:
        return None