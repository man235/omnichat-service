from datetime import datetime
from typing import Union, Any
from django.conf import settings

import requests
from rest_framework.response import Response

from sop_chat_service.zalo.utils.response_templates import json_response


def get_oa_token(oa_id: Union[int, str] = None, 
                 authorization_code: str = None, 
                 code_verifier: str = None,
                 refresh_token: str = None,
                ) -> Any:
    """
    Get OA token
    """
    oa_oauth_url = settings.ZALO_OA_OAUTH_API
    try: 
        if refresh_token:
            payload = {
                'app_id': settings.ZALO_APP_ID,
                'grant_type': 'refresh_token',
                'refresh_token': refresh_token
            }
        else:
            payload = {
                'oa_id': oa_id,
                'code': authorization_code,
                'app_id': settings.ZALO_APP_ID,
                'grant_type': 'authorization_code',
                'code_verifier': code_verifier
            }

        url = f'{oa_oauth_url}/access_token'
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'secret_key': settings.ZALO_APP_SECRET_KEY
        }
        oa_token_rp = requests.post(url=url,
                                    data=payload, 
                                    headers=headers)
    
        if oa_token_rp.status_code == 200:
            oa_token_json = oa_token_rp.json()
                
            if oa_token_json.get('access_token'):
                return json_response(is_success=True, result=oa_token_json)
            else:
                return json_response(is_success=False, result=oa_token_json)
        else:
            return None  # BAD Request
    except Exception as e:  
        return json_response(is_success=False, result=e)
    
def get_oa_info(access_token: str = None) -> Response:
    """
    Utility function gets OA's informations
    """
    if access_token:
        url = f'{settings.ZALO_OA_OPEN_API}/getoa'
        headers = {'access_token': access_token}
        oa_info_reponse = requests.get(url=url, headers=headers)  
           
        return oa_info_reponse
    
def check_valid_token(time_update: datetime = None) -> tuple:
    """
    Utility function check valid token by time remaining
    """
    try:
        now = datetime.now()
        diff = now - time_update
        time_remaining = diff.seconds
        expired_atk = False
        expired_rtk = False
        
        if time_remaining > settings.OA_ACCESS_EXPIRED_IN:
            expired_atk = True
        if time_remaining > settings.OA_REFRESH_EXPIRED_IN:
            expired_rtk = True
        return expired_atk, expired_rtk
    except Exception:
        return None
