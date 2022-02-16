import jwt

from django.conf import settings
from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from rooms.models import Room
from rooms.serializers import RoomSerializer
from .models import User
from .serializers import UserSerializer


class UsersView(APIView):
    """
    유저 생성하기
    """
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            new_user = serializer.save()
            return Response(UserSerializer(new_user).data)
        else:
            return Response(serializer.error, status=status.HTTP_400_BAD_REQUEST)


class MeView(APIView):
    """
    로그인한 유저 정보 가져오기
    로그인한 유저 정보 수정하기
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)

    def put(self, request):
        serializer = UserSerializer(request.user, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.error, status=status.HTTP_400_BAD_REQUEST)


class FavsView(APIView):
    """
    로그인한 유저 favs 가져오기
    로그인한 유저 favs에 방 추가/삭제하기
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = RoomSerializer(request.user.favs.all(), many=True).data
        return Response(serializer)

    def put(self, request):
        pk = request.data.get("pk", None)
        if pk is not None:
            try:
                room = Room.objects.get(pk=pk)
                if room in request.user.favs.all():
                    request.user.favs.remove(room)
                else:
                    request.user.favs.add(room)
                return Response()
            except Room.DoesNotExist:
                pass

        return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
def user_detail(request, pk):
    """
    유저 정보 가져오기
    """
    try:
        user = User.objects.get(pk=pk)
        return Response(UserSerializer(user).data)
    except User.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)


@api_view(["POST"])
def login(request):
    """
    로그인 성공 시 jwt 발급
    """
    username = request.data.get("username")
    password = request.data.get("password")

    if not username or not password:
        return Response(status=status.HTTP_400_BAD_REQUEST)

    user = authenticate(username=username, password=password)

    if user is not None:
        encoded_jwt = jwt.encode({"pk": user.pk}, settings.SECRET_KEY, algorithm="HS256")
        return Response(data={"token": encoded_jwt})
    else:
        return Response(status=status.HTTP_401_UNAUTHORIZED)
