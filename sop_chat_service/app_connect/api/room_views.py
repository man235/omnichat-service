from datetime import datetime
from django.conf import settings
from rest_framework import serializers, viewsets, permissions, status, mixins
from rest_framework.response import Response
from sop_chat_service.app_connect.api.room_serializers import RoomSerializer
from sop_chat_service.app_connect.models import Room
from rest_framework.decorators import action
from django.utils import timezone


class RoomViewSet(viewsets.ModelViewSet):

    serializer_class = RoomSerializer
    queryset = Room.objects.all()
    permission_classes = (permissions.AllowAny, )

    @action(detail=True, methods=["POST"], url_path="complete")
    def complete_room(self, request, pk=None, *args, **kwargs):
        room = Room.objects.get(id=pk)
        room.completed_date = datetime.now(tz=timezone.utc)
        room.save()
        return Response(status=status.HTTP_200_OK)
