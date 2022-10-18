from rest_framework import status, generics
from rest_framework.permissions import AllowAny
import time, datetime
from sop_chat_service.facebook.utils import custom_response


class ServiceInfoView(generics.GenericAPIView):
    permission_classes = (AllowAny, )
    def get(self, request, *args, **kwargs):
        data = {
            "status":"running",
            "info":{
                "name":"auth-service",
                "port":4001,
                "code":"expressjs"
            },
            "date": datetime.datetime.now()
            }
        return custom_response(status.HTTP_200_OK, "OK", data)
