from django.conf import settings
from rest_framework import viewsets, permissions, status, serializers
from rest_framework.response import Response
from rest_framework.decorators import action
from sop_chat_service.app_connect.serializers.label_serializers import LabelSerializer, CreateLabelSerializer, UpdateLabelSerializer
from sop_chat_service.app_connect.models import Label, Room


class LabelViewSet(viewsets.ModelViewSet):
    queryset = Label.objects.all()
    permission_classes = (permissions.AllowAny, )
    serializer_class = LabelSerializer

    def create(self, request, *args, **kwargs):
        data = request.data
        serializer = CreateLabelSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            room = Room.objects.get(id=data['room_id'])
            if not room:
                serializers.ValidationError({"room": "Room is not valid"})
            else:
                Label.objects.create(
                    room_id=room,
                    name=data['name'],
                    color=data['color']
                )
                return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, pk=None, *args, **kwargs):
        data = request.data
        serializer = UpdateLabelSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            label = Label.objects.get(id=pk)
            label.name = data['name']
            label.color = data['color']
            label.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
