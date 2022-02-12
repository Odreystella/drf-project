from rest_framework import status
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from rooms.models import Room
from rooms.serializers import RoomSerializer
from .serializers import UserSerializer
from .models import User


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
