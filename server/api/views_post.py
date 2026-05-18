import re
from datetime import datetime, timedelta

from django.db import IntegrityError
from django.db.models import Q
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .authentication import verify_token
from .models import Post
from .utils import ApiError


def _slugify(title):
    slug = title.split(' ')
    slug = '-'.join(slug).lower()
    slug = re.sub(r'[^a-zA-Z0-9-]', '', slug)
    return slug


@api_view(['POST'])
@verify_token
def create(request):
    auth_user = request.auth_user
    if not auth_user.get('isAdmin'):
        raise ApiError(403, 'You are not allowed to create a post')

    data = request.data
    if not data.get('title') or not data.get('content'):
        raise ApiError(400, 'Please provide all required fields')

    slug = _slugify(data['title'])

    post_kwargs = {
        'title': data['title'],
        'content': data['content'],
        'slug': slug,
        'user_id': str(auth_user.get('id')),
    }
    if data.get('image'):
        post_kwargs['image'] = data['image']
    if data.get('category'):
        post_kwargs['category'] = data['category']

    try:
        post = Post.objects.create(**post_kwargs)
    except IntegrityError:
        raise ApiError(400, 'A post with that title already exists')

    return Response(post.to_dict(), status=201)


@api_view(['GET'])
def getposts(request):
    q = request.query_params
    start_index = int(q.get('startIndex', 0))
    limit = int(q.get('limit', 9))
    sort_direction = '-updated_at' if q.get('order') != 'asc' else 'updated_at'

    posts = Post.objects.all()
    if q.get('userId'):
        posts = posts.filter(user_id=q.get('userId'))
    if q.get('category'):
        posts = posts.filter(category=q.get('category'))
    if q.get('slug'):
        posts = posts.filter(slug=q.get('slug'))
    if q.get('postId'):
        posts = posts.filter(id=q.get('postId'))
    if q.get('searchTerm'):
        term = q.get('searchTerm')
        posts = posts.filter(Q(title__icontains=term) | Q(content__icontains=term))

    posts = posts.order_by(sort_direction)[start_index:start_index + limit]

    total_posts = Post.objects.count()
    one_month_ago = datetime.utcnow() - timedelta(days=30)
    last_month_posts = Post.objects.filter(created_at__gte=one_month_ago).count()

    return Response({
        'posts': [p.to_dict() for p in posts],
        'totalPosts': total_posts,
        'lastMonthPosts': last_month_posts,
    })


@api_view(['DELETE'])
@verify_token
def deletepost(request, post_id, user_id):
    auth_user = request.auth_user
    if not auth_user.get('isAdmin') or str(auth_user.get('id')) != str(user_id):
        raise ApiError(403, 'You are not allowed to delete this post')

    Post.objects.filter(id=post_id).delete()
    return Response('The post has been deleted')


@api_view(['PUT'])
@verify_token
def updatepost(request, post_id, user_id):
    auth_user = request.auth_user
    if not auth_user.get('isAdmin') or str(auth_user.get('id')) != str(user_id):
        raise ApiError(403, 'You are not allowed to update this post')

    try:
        post = Post.objects.get(id=post_id)
    except Post.DoesNotExist:
        raise ApiError(404, 'Post not found')

    data = request.data
    post.title = data.get('title', post.title)
    post.content = data.get('content', post.content)
    post.category = data.get('category', post.category)
    post.image = data.get('image', post.image)
    post.save()

    return Response(post.to_dict())
