import jwt

from django.conf import settings
from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAdminUser, AllowAny

from rooms.models import Room
from rooms.serializers import RoomSerializer
from .models import User
from .serializers import UserSerializer
from .permissions import IsMe


class UsersViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
        print(self.action)
        permission_classes = []
        if self.action == "list":
            permission_classes = [IsAdminUser]
        elif (
            self.action == "create" 
            or self.action =="retrieve" 
            or self.action == "favs"
        ):
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsMe]
        return [permission() for permission in permission_classes]

    @action(detail=False, methods=["POST"])
    def login(self, request):
        """
        로그인 (성공 시 jwt 발급)
        """
        username = request.data.get("username")
        password = request.data.get("password")
        if not username or not password:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        user = authenticate(username=username, password=password)
        if user is not None:
            encoded_jwt = jwt.encode(
                {"pk": user.pk}, settings.SECRET_KEY, algorithm="HS256"
            )
            return Response(data={"token": encoded_jwt, "id": user.pk})
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

    @action(detail=True)   # /api/v1/users/1/favs/, AllowAny
    def favs(self, request, pk):
        """
        로그인한 유저 favs 가져오기
        """
        user = self.get_object()
        serializer = RoomSerializer(user.favs.all(), many=True).data
        return Response(serializer)

    @favs.mapping.put     # /api/v1/users/1/favs/, IsMe
    def toggle_favs(self, request, pk):
        """
        로그인한 유저 favs에 방 추가/삭제하기
        """
        pk = request.data.get("pk", None)
        user = self.get_object()
        if pk is not None:
            try:
                room = Room.objects.get(pk=pk)
                if room in user.favs.all():
                    user.favs.remove(room)
                else:
                    user.favs.add(room)
                return Response()
            except Room.DoesNotExist:
                pass
        return Response(status=status.HTTP_400_BAD_REQUEST)
