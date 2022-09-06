from datetime import datetime
from django.conf import settings
from rest_framework import serializers, viewsets, permissions, status, mixins
from rest_framework.response import Response
from sop_chat_service.app_connect.api.room_serializers import RoomMessageSerializer, RoomSerializer
from sop_chat_service.app_connect.models import Room
from rest_framework.decorators import action
from django.utils import timezone

from sop_chat_service.facebook.utils import custom_response


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
    def list(self, request, *args, **kwargs):
        qs = Room.objects.filter(room_message__is_sender=False, completed_date__isnull=True).order_by(
        '-created_at')
        if 'type' in request.query_params:
            type = request.query_params['type']
            qs = qs.filter(type=request.query_params['type'])
            if 'status' in request.query_params:
                filter = request.query_params['status']
                if filter.lower() == 'waiting':
                    qs = qs.filter(type=request.query_params['type'], approved_date__isnull=True)
                elif filter.lower() == 'processing':
                    qs = qs.filter(type=request.query_params['type'],
                                   approved_date__isnull=False, completed_date__isnull=True)
        elif 'status' in request.query_params:
            filter = request.query_params['status']
            if filter.lower() == 'waiting':
                qs = qs.filter(approved_date__isnull=True)
            elif filter.lower() == 'processing':
                qs = qs.filter(approved_date__isnull=False, completed_date__isnull=True)
        elif 'name' in request.query_params:
            qs = qs.filter(name__icontains=request.query_params['name'])
        sz = RoomMessageSerializer(qs, many=True)
        return custom_response(200, "Get List Room Successfully", sz.data)
        