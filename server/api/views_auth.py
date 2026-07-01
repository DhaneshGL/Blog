import random
import string

import jwt
from django.conf import settings
from django.contrib.auth.hashers import check_password, make_password
from django.db import IntegrityError
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import User
from .utils import ApiError, set_auth_cookie


def _make_token(user_id, is_admin):
    return jwt.encode({'id': user_id, 'isAdmin': is_admin}, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


@api_view(['POST'])
def signup(request):
    username = request.data.get('username')
    email = request.data.get('email')
    password = request.data.get('password')

    if not username or not email or not password:
        raise ApiError(400, 'All fields are required')

    hashed_password = make_password(password)

    try:
        User.objects.create(username=username, email=email, password=hashed_password)
    except IntegrityError:
        raise ApiError(400, 'Username or email already in use')

    return Response('Signup successful')


@api_view(['POST'])
def signin(request):
    email = request.data.get('email')
    password = request.data.get('password')

    if not email or not password:
        raise ApiError(400, 'All fields are required')

    try:
        valid_user = User.objects.get(email=email)
    except User.DoesNotExist:
        raise ApiError(404, 'User not found')

    if not check_password(password, valid_user.password):
        raise ApiError(400, 'Invalid password')

    token = _make_token(valid_user.id, valid_user.is_admin)

    response = Response(valid_user.to_public_dict(), status=200)
    set_auth_cookie(response, token, settings.SHORT_COOKIE_MAX_AGE)
    return response


@api_view(['POST'])
def google(request):
    email = request.data.get('email')
    name = request.data.get('name')
    google_photo_url = request.data.get('googlePhotoUrl')

    try:
        user = User.objects.get(email=email)
        token = _make_token(user.id, user.is_admin)
        response = Response(user.to_public_dict(), status=200)
        set_auth_cookie(response, token, settings.SHORT_COOKIE_MAX_AGE)
        return response
    except User.DoesNotExist:
        generated_password = ''.join(random.choices(string.ascii_lowercase + string.digits, k=16))
        hashed_password = make_password(generated_password)
        generated_username = name.lower().replace(' ', '') + ''.join(random.choices(string.digits, k=4))
        new_user = User.objects.create(
            username=generated_username,
            email=email,
            password=hashed_password,
            profile_picture=google_photo_url,
        )
        token = _make_token(new_user.id, new_user.is_admin)
        response = Response(new_user.to_public_dict(), status=200)
        response.set_cookie(key='access_token', value=token, httponly=True)
        return response
