from rest_framework import serializers

from users.serializers import RelatedUserSerializer
from .models import Room


class RoomSerializer(serializers.ModelSerializer):
    user = RelatedUserSerializer()

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
