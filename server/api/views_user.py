import re
from datetime import datetime, timedelta

from django.contrib.auth.hashers import make_password
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .authentication import verify_token
from .models import User
from .utils import ApiError


@api_view(['GET'])
def test(request):
    return Response({'message': 'API is working!'})


@api_view(['PUT'])
@verify_token
def update_user(request, user_id):
    data = request.data

    password = data.get('password')
    if password:
        if len(password) < 6:
            raise ApiError(400, 'Password must be at least 6 characters')
        password = make_password(password)

    username = data.get('username')
    if username:
        if len(username) < 7 or len(username) > 20:
            raise ApiError(400, 'Username must be between 7 and 20 characters')
        if ' ' in username:
            raise ApiError(400, 'Username cannot contain spaces')
        if username != username.lower():
            raise ApiError(400, 'Username must be lowercase')
        if not re.match(r'^[a-zA-Z0-9]+$', username):
            raise ApiError(400, 'Username can only contain letters and numbers')

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        raise ApiError(404, 'User not found')

    if username is not None:
        user.username = username
    if 'email' in data:
        user.email = data.get('email')
    if 'profilePicture' in data:
        user.profile_picture = data.get('profilePicture')
    if password:
        user.password = password
    user.save()

    return Response(user.to_public_dict())


@api_view(['DELETE'])
@verify_token
def delete_user(request, user_id):
    auth_user = request.auth_user
    if not auth_user.get('isAdmin') and str(auth_user.get('id')) != str(user_id):
        raise ApiError(403, 'You are not allowed to delete this user')

    User.objects.filter(id=user_id).delete()
    return Response('User has been deleted')


@api_view(['POST'])
def signout(request):
    response = Response('User has been signed out')
    response.delete_cookie('access_token')
    return response


@api_view(['GET'])
@verify_token
def get_users(request):
    auth_user = request.auth_user
    if not auth_user.get('isAdmin'):
        raise ApiError(403, 'You are not allowed to see all users')

    start_index = int(request.query_params.get('startIndex', 0))
    limit = int(request.query_params.get('limit', 9))
    sort_direction = '-created_at' if request.query_params.get('sort') != 'asc' else 'created_at'

    users = User.objects.order_by(sort_direction)[start_index:start_index + limit]
    total_users = User.objects.count()

    now = datetime.utcnow()
    one_month_ago = now - timedelta(days=30)
    last_month_users = User.objects.filter(created_at__gte=one_month_ago).count()

    return Response({
        'users': [u.to_public_dict() for u in users],
        'totalUsers': total_users,
        'lastMonthUsers': last_month_users,
    })


@api_view(['GET'])
def get_user(request, user_id):
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        raise ApiError(404, 'User not found')

    return Response(user.to_public_dict())
