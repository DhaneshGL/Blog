from django.urls import path

from . import views_post

urlpatterns = [
    path('create', views_post.create),
    path('getposts', views_post.getposts),
    path('deletepost/<str:post_id>/<str:user_id>', views_post.deletepost),
    path('updatepost/<str:post_id>/<str:user_id>', views_post.updatepost),
]
