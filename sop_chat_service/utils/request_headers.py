
def get_user_from_header(header):
    user_id = header.get('X-Auth-User-Id')
    return user_id
