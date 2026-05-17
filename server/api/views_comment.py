from datetime import datetime, timedelta

from rest_framework.decorators import api_view
from rest_framework.response import Response

from .authentication import verify_token
from .models import Comment
from .utils import ApiError


@api_view(['POST'])
@verify_token
def create_comment(request):
    data = request.data
    content = data.get('content')
    post_id = data.get('postId')
    user_id = data.get('userId')

    if str(user_id) != str(request.auth_user.get('id')):
        raise ApiError(403, 'You are not allowed to create this comment')

    comment = Comment.objects.create(content=content, post_id=post_id, user_id=user_id)
    return Response(comment.to_dict())


@api_view(['GET'])
def get_post_comments(request, post_id):
    comments = Comment.objects.filter(post_id=post_id).order_by('-created_at')
    return Response([c.to_dict() for c in comments])


@api_view(['PUT'])
@verify_token
def like_comment(request, comment_id):
    try:
        comment = Comment.objects.get(id=comment_id)
    except Comment.DoesNotExist:
        raise ApiError(404, 'Comment not found')

    user_id = str(request.auth_user.get('id'))
    likes = comment.likes or []
    if user_id not in likes:
        comment.number_of_likes += 1
        likes.append(user_id)
    else:
        comment.number_of_likes -= 1
        likes.remove(user_id)
    comment.likes = likes
    comment.save()

    return Response(comment.to_dict())


@api_view(['PUT'])
@verify_token
def edit_comment(request, comment_id):
    try:
        comment = Comment.objects.get(id=comment_id)
    except Comment.DoesNotExist:
        raise ApiError(404, 'Comment not found')

    auth_user = request.auth_user
    if str(comment.user_id) != str(auth_user.get('id')) and not auth_user.get('isAdmin'):
        raise ApiError(403, 'You are not allowed to edit this comment')

    comment.content = request.data.get('content', comment.content)
    comment.save()

    return Response(comment.to_dict())


@api_view(['DELETE'])
@verify_token
def delete_comment(request, comment_id):
    try:
        comment = Comment.objects.get(id=comment_id)
    except Comment.DoesNotExist:
        raise ApiError(404, 'Comment not found')

    auth_user = request.auth_user
    if str(comment.user_id) != str(auth_user.get('id')) and not auth_user.get('isAdmin'):
        raise ApiError(403, 'You are not allowed to delete this comment')

    comment.delete()
    return Response('Comment has been deleted')


@api_view(['GET'])
@verify_token
def getcomments(request):
    auth_user = request.auth_user
    if not auth_user.get('isAdmin'):
        raise ApiError(403, 'You are not allowed to get all comments')

    q = request.query_params
    start_index = int(q.get('startIndex', 0))
    limit = int(q.get('limit', 9))
    sort_direction = '-created_at' if q.get('sort') == 'desc' else 'created_at'

    comments = Comment.objects.order_by(sort_direction)[start_index:start_index + limit]
    total_comments = Comment.objects.count()
    one_month_ago = datetime.utcnow() - timedelta(days=30)
    last_month_comments = Comment.objects.filter(created_at__gte=one_month_ago).count()

    return Response({
        'comments': [c.to_dict() for c in comments],
        'totalComments': total_comments,
        'lastMonthComments': last_month_comments,
    })
