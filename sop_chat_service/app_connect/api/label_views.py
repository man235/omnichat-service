from django.conf import settings
from rest_framework import viewsets, permissions, status, serializers
from rest_framework.response import Response
from rest_framework.decorators import action
from sop_chat_service.app_connect.serializers.label_serializers import LabelSerializer, CreateLabelSerializer, UpdateLabelSerializer
from sop_chat_service.app_connect.models import Label, Room
from sop_chat_service.facebook.utils import custom_response

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
                label =Label.objects.create(
                    room_id=room,
                    name=data['name'],
                    color=data['color']
                )
                sz = LabelSerializer(label,many=False)
                return custom_response(200, "Create Label Successfully",sz.data)

    def update(self, request, pk=None, *args, **kwargs):
        data = request.data
        print(data)
        label = Label.objects.get(id=pk)
        serializer = LabelSerializer(label,data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()    
        return custom_response(200,"Update Label Successfully",serializer.data)