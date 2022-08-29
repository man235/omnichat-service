from rest_framework.response import Response
from rest_framework import status


def custom_response(status_code=status.HTTP_200_OK, message='', data=[]):
    return Response(
        {
            "status": status_code,
            "message": message,
            "data": data
        },
        status=status_code)
