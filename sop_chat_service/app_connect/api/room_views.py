from datetime import datetime
from django.conf import settings
from rest_framework import serializers, viewsets, permissions, status, mixins
from rest_framework.response import Response
from sop_chat_service.app_connect.api.room_serializers import RoomMessageSerializer, RoomSerializer
from sop_chat_service.app_connect.models import Attachment, FanPage, Message, Room
from rest_framework.decorators import action
import requests


class RoomViewSet(viewsets.ModelViewSet):

    serializer_class = RoomSerializer
    queryset = Room.objects.all()
    permission_classes = (permissions.AllowAny, )
