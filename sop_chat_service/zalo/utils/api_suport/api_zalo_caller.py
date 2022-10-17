from asyncio import constants
from email import header
import json
from typing import Any
from django.conf import settings
from sop_chat_service.zalo.utils.chat_support.type_constant import *
import requests
from .response_templates import json_response


def get_oa_follower(user_id: Any=None, access_token: str=None) -> Any:
    """
    Utility function to get the information of Zalo OA follower
    """
    try:
        # or url = '{0}/getprofile?data={1}'.format(settings.ZALO_OA_OPEN_API, {"user_id": user_id})
        url = f'{settings.ZALO_OA_OPEN_API}/getprofile?data={{"user_id": {user_id}}}'
        headers = {
            'access_token': access_token,
        }
        payload = {}
        oa_follower_rp = requests.get(url=url, headers=headers)
        oa_follower = oa_follower_rp.json()
        if oa_follower_rp.status_code == 200:
            if oa_follower.get('message') == 'Success':
                return json_response(True, oa_follower.get('data'))
            return json_response(False, oa_follower.get('message'))
        else:
            return None     # Bad request
    except Exception as e:
        return json_response(False, str(e))
 
    
def request_shared_info(user_id: str, access_token: str, message: Any = None) -> Any:
    """
    Utility function to request the shared information from unfollowed user zalo app
    """
    try:
        url = f'{settings.ZALO_OA_OPEN_API}/message'
        headers = {
            'Content-Type': 'application/json',
            'access_token': access_token,
        }
        payload = {
            'recipient': {
                'user_id': user_id,
            },
            'message': {
                'attachment': {
                    'type': 'template',
                    'payload': {
                        'template_type': 'request_user_info',
                        'elements': [{
                            'title': 'OA Chatbot (Testing)',
                            'subtitle': 'Đang yêu cầu thông tin từ bạn',
                            'image_url': 'https://developers.zalo.me/web/static/zalo.png'
                        }]
                    }
                }
            },
        }
        
        user_shared_info_rp = requests.post(url=url, headers=headers, data=payload)
        user_shared_info = user_shared_info_rp.json()
        
        if user_shared_info_rp.status_code == 200:
            if user_shared_info.get('message') == 'Success':
                return json_response(True, user_shared_info.get('data'))
            
            return json_response(False, user_shared_info)
        else:
            return None     # Bad request
    except Exception as e:
        return json_response(False, str(e))


def send_zalo_message(
    msg_type: str = TEXT_MESSAGE,
    access_token: str = None,
    recipient_id: str = None,
    text: str = None,
    attachment_token: str = None,
    attachment_id: str = None,
) -> dict:
    
    message = {}
    if msg_type == TEXT_MESSAGE:
        message: dict = {
            'text': text
        }
    elif msg_type == FILE_MESSAGE:
        message = {
            "attachment": {
            "type": "file",
            "payload": {
                "token": attachment_token,
            }
        }
    }
    elif msg_type in (STICKER_MESSAGE, IMAGE_MESSAGE):
        message = {
            "attachment": {
                "type": "template",
                "payload": {
                    "template_type": "media",
                    "elements": [{
                        "media_type": msg_type,
                            "attachment_id": attachment_id
                    }]
                }
            }
        }
        
    rp = requests.post(
        url = f'{settings.ZALO_OA_OPEN_API}/message',
        headers = {
            "Content-Type": 'application/json',
            "access_token": access_token,    
        },
        data = json.dumps({
            "recipient": {
                "user_id": str(recipient_id),
            },
            "message": message,
        })
    )
    
    if rp.status_code == 200:
        rp_json = rp.json()
        
        if rp_json.get('message') == 'Success':
            return json_response(True, rp_json.get('data'))
        else:
            return json_response(False, rp_json.get('message'))
    else:
        return None # BAD Request


def upload_zalo_attachment(
    attachment_type: str = FILE_MESSAGE,
    access_token: str = None,
    attachment: Any = None,
) -> dict:
        
    rp = requests.post(
        url = f'{settings.ZALO_OA_OPEN_API}/upload/{attachment_type}',
        headers = {
            # 'Content-Type': 'application/pdf',
            'access_token': access_token
        },
        files = [
            ('file', (attachment.name, attachment, attachment.content_type))
        ]
    )
    
    if rp.status_code == 200:
        rp_json = rp.json()
        
        if rp_json.get('message') == 'Success':
            return json_response(True, rp_json.get('data'))
        else:
            return json_response(False, rp_json.get('message'))
    else:
        return None # BAD Request
    
    
def get_message_data_of_zalo_user(
    access_token: str = None,
    user_id: str = None,
    offset: int = 0,
    count: int = 1,
) -> Any:
    """
    Utility function to get conversation data among Zalo OA and specific it's follower.
    Need to test as user is not a follower (anonymous user).
    Note:
        - `offset`: the order of the first message. the latest message has offest = 0
        - `count`: amount of messages want to get
    """
    
    rp = requests.get(
        url = f'{settings.ZALO_OA_OPEN_API}/conversation',
        headers = {
            'access_token': access_token,
        },
        params = {
            'data': {
                'user_id': user_id,
                'offset': offset,
                'count': count,
            }
        }
    )
    
    if rp.status_code == 200:
        rp_json = rp.json()
        
        if rp_json.get('message') == 'Success':
            return json_response(True, rp_json.get('data'))
        else:
            return json_response(False, rp_json)
    else:
        return None # BAD Request

    