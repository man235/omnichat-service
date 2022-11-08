from django.conf import settings
from rest_framework import viewsets, permissions, status, serializers
from rest_framework.response import Response
from rest_framework.decorators import action
from sop_chat_service.app_connect.serializers.label_serializers import LabelSerializer, CreateLabelSerializer, GetLabelSerializer
from sop_chat_service.app_connect.models import Label, Room
from sop_chat_service.facebook.utils import custom_response
from sop_chat_service.utils.request_headers import get_user_from_header

class LabelViewSet(viewsets.ModelViewSet):
    queryset = Label.objects.all()
    permission_classes = (permissions.AllowAny, )
    serializer_class = LabelSerializer
    # def list(self,request,*args, **kwargs):
    #     serializer = GetLabelSerializer(data=request.data)
    #     room,user = serializer.validate(request ,request.data)
    #     if not room:
    #         return custom_response(400,"Invalid Room",[])
    #     label = Label.objects.filter(room_id =room)
    #     sz = LabelSerializer(label)
    #     return custom_response(200,"Get List Label Successfully",sz.data)
    def create(self, request, *args, **kwargs):
        data = request.data
        serializer = CreateLabelSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            room = Room.objects.get(room_id=data['room_id'])
            if not room:
                serializers.ValidationError({"room": "Room is not valid"})
            else:
                label =Label.objects.create(
                    room_id=room,
                    label_id=data['label_id']
                )
                sz = LabelSerializer(label,many=False)
                return custom_response(200, "Create Label Successfully",sz.data)

    def destroy(self, request, pk=None, *args, **kwargs):
        label = Label.objects.get(id=pk).delete()
        return custom_response(200,"Remove Label Successfully",[])
