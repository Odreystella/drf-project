from rest_framework import serializers

from .models import User


class RelatedUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "username", 
            "first_name", 
            "last_name", 
            "email", 
            "avatar", 
            "superhost"
            )


class ReadUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id", 
            "username", 
            "first_name", 
            "last_name", 
            "email", 
            "avatar", 
            "superhost",
            "favs"
            )


class WriteUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "username", 
            "first_name", 
            "last_name", 
            "email"
        )

    def validate_first_name(self, value):
        return value.title()

