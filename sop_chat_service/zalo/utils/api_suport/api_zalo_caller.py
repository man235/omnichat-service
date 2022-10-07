from typing import Any
from django.conf import settings
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