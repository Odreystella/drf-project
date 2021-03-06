import jwt

from django.conf import settings
from rest_framework import authentication
from rest_framework import exceptions

from users.models import User


class JWTAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        try:
            token = request.META.get("HTTP_AUTHORIZATION")
            if token is None:
                return None
            xjwt, jwt_token = token.split(" ")
            decoded_jwt = jwt.decode(jwt_token, settings.SECRET_KEY, \
                algorithms=["HS256"])
            user = User.objects.get(pk=decoded_jwt.get("pk"))
            return (user, None)
        except ValueError:
            return None
        except jwt.exceptions.DecodeError:
            raise exceptions.AuthenticationFailed(detail="JWT Format Invalid")
        except User.DoesNotExist:
            return None
