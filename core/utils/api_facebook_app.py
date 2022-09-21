from django.conf import settings
import requests, json


def get_user_info(user_id, access_token):
    fb_graph_api = settings.FACEBOOK_GRAPH_API
    fields_query = settings.PROFILE_USER_FIELDS
    try:
        params = {'fields': fields_query, 'access_token': access_token}
        response = requests.get(f'{fb_graph_api}/{user_id}/', params=params)

        if response.status_code == 200:
            return response.json()
        else:
            return None
    except Exception as e:
        return None


def api_send_message_text_facebook(access_token, data):
    url =f'{settings.URL_FACEBOOK_GRAPH_API_SEND_MESSAGE}?access_token={access_token}'
    headers = {
        'Content-Type': 'application/json',
    }
    try:
        response = requests.post(url, headers= headers, data=json.dumps(data))
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except Exception as e:
        return None


def api_send_message_file_facebook(access_token, data, file):
    url =f'{settings.URL_FACEBOOK_GRAPH_API_SEND_MESSAGE}?access_token={access_token}'
    headers = {}
    try:
        response = requests.post(url, headers= headers, data=data['payload'], files=file)
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except Exception as e:
        return None


def get_message_from_mid(access_token, mid):
    graph_api = settings.FACEBOOK_GRAPH_API
    query_field = {
        'access_token': access_token,
        'fields': 'message,created_time,from,to,attachments'
    }
    try:
        response = requests.get(f'{graph_api}/{mid}/', params=query_field)
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except Exception as e:
        response = requests.get(f'{graph_api}/{mid}/', params=query_field)
        if response.status_code == 200:
            return response
        else:
            return None
