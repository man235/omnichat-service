from datetime import datetime
from django.conf import settings
from rest_framework import serializers, viewsets, permissions, status
from rest_framework.response import Response
from sop_chat_service.app_connect.api.room_serializers import RoomSerializer
from sop_chat_service.app_connect.serializers.room_serializers import RoomMessageSerializer, GetMessageSerializer
from sop_chat_service.app_connect.serializers.message_serializers import MessageSerializer
from sop_chat_service.app_connect.models import Room, Message
from sop_chat_service.facebook.utils import custom_response
from rest_framework.decorators import action
from django.utils import timezone

from sop_chat_service.facebook.utils import custom_response


class RoomViewSet(viewsets.ModelViewSet):

    serializer_class = RoomSerializer
    queryset = Room.objects.all()
    permission_classes = (permissions.AllowAny, )

    def retrieve(self, request, pk=None):
        room = Room.objects.get(id =pk)
        if room & room.is_active == True:
            message = Message.objects.filter(room_id = room)
            sz= MessageSerializer(message,many=True)
        return custom_response(200,"Get Message Successfully",sz.data)

    def create(self, request, *args, **kwargs):
        pass

    def post(self, request, *args, **kwargs):
        pass

    def list(self, request, *args, **kwargs):
        # qs = Room.objects.filter(room_message__is_sender=False, completed_date__isnull=True).order_by('-created_at')
        qs = Room.objects.filter().order_by('-created_at')
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
        