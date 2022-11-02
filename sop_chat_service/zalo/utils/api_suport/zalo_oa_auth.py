from typing import Union, Any
from django.conf import settings
from .response_templates import json_response
import requests


def get_oa_token(
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
                'code': authorization_code,
                'app_id': settings.ZALO_APP_ID,
                'grant_type': 'authorization_code',
            }
            
            if code_verifier != None:
                payload['code_verifier'] = code_verifier

        url = f'{oa_oauth_url}/access_token'
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'secret_key': settings.ZALO_APP_SECRET_KEY
        }
        oa_token_rp = requests.post(
            url=url,
            data=payload, 
            headers=headers,
            timeout=(5, 10)
        )
    
        if oa_token_rp.status_code == 200:
            oa_token_json = oa_token_rp.json()
                
            if oa_token_json.get('access_token'):
                return json_response(is_success=True, result=oa_token_json)
            else:
                return json_response(is_success=False, result=oa_token_json)
        else:
            return None  # BAD Request
    except Exception as e:  
        return json_response(is_success=False, result=str(e))
    
    
def get_oa_info(access_token: str = None) -> Any:
    """
    Utility function gets OA's informations v2.0 - return json data
    """
    if access_token:
        try:
            url = f'{settings.ZALO_OA_OPEN_API}/getoa'
            headers = {'access_token': access_token}
            oa_info_reponse = requests.get(
                url=url,
                headers=headers,
                timeout=(5, 10)
            )  
            
            oa_info_json = oa_info_reponse.json()

            if oa_info_reponse.status_code == 200:
                if oa_info_json.get('message') == 'Success':
                    oa_data: dict = oa_info_json.get('data')
                    oa_data_bundle = {
                        'page_id': oa_data.get('oa_id'),
                        'name': oa_data.get('name'),
                        'avatar_url': oa_data.get('avatar'),
                        'is_active': True,
                    }
                    return json_response(is_success=True, result=oa_data_bundle)
                else:
                    return json_response(is_success=False, result=oa_info_json)
            else:
                return None
        except Exception as e:
            return json_response(is_success=False, result=str(e)) 
    