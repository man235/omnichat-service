
def get_user_from_header(header):
    user_id = header.get('X-Auth-Id')
    return user_id
