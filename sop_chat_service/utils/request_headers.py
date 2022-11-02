
def get_user_from_header(header):
    user_id = header.get('X-Auth-User-Id')
    return user_id
def get_email_from_header(header):
    user_email = header.get('X-Auth-Email')
    return user_email
