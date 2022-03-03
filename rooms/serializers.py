from rest_framework import serializers
from users.serializers import UserSerializer

from .models import Room


class RoomSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    is_fav = serializers.SerializerMethodField(method_name="get_your_fav_list")

    class Meta:
        model = Room
        exclude = ("created",)
        read_only_fields = ("user", "id", "created", "modified")

    def validate(self, data):
        if self.instance:      # update
            check_in = data.get("check_in", self.instance.check_in)
            check_out = data.get("check_out", self.instance.check_out)
        else:                  # create
            check_in = data.get("check_in")
            check_out = data.get("check_out")

        if check_in == check_out:
            raise serializers.ValidationError("Not enouth time between times")
        return data

    def get_your_fav_list(self, obj):
        request = self.context.get("request")
        if request:
            user = request.user
            if user.is_authenticated:
                return obj in user.favs.all()
        return False

    def create(self, validated_data):
        user = self.context.get("request").user
        room = Room.objects.create(**validated_data, user=user)
        return room
