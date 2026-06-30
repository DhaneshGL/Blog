from functools import wraps

import jwt
from django.conf import settings

from .utils import ApiError


def verify_token(view_func):

    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        token = request.COOKIES.get('access_token')
        if not token:
            raise ApiError(401, 'Unauthorized')
        try:
            payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        except jwt.PyJWTError:
            raise ApiError(401, 'Unauthorized')
        request.auth_user = payload
        return view_func(request, *args, **kwargs)

    return wrapper
