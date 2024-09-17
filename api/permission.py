import jwt
from functools import wraps
from api.models import UserData
from rest_framework.views import APIView
from rest_framework.exceptions import AuthenticationFailed

secret = os.environ.get('secret')

def CheckAuth(func):
    def wrapper(request, *args, **kwargs):
        if request.headers.get('Authorization'):
            token = request.headers['Authorization']
            if not token:
                raise AuthenticationFailed('Unauthenticated')
            try:
                payload = jwt.decode(token, secret, algorithms=['HS256'])
                return func(request, *args, **kwargs)
            except jwt.ExpiredSignatureError:
                raise AuthenticationFailed('Unauthenticated')
        else:
            raise AuthenticationFailed('Unauthenticated')
    return wrapper

