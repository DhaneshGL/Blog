from django.urls import path

from . import views_comment

urlpatterns = [
    path('create', views_comment.create_comment),
    path('getPostComments/<str:post_id>', views_comment.get_post_comments),
    path('likeComment/<str:comment_id>', views_comment.like_comment),
    path('editComment/<str:comment_id>', views_comment.edit_comment),
    path('deleteComment/<str:comment_id>', views_comment.delete_comment),
    path('getcomments', views_comment.getcomments),
]
