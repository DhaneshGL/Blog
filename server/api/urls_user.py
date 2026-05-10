from django.urls import path

from . import views_user

urlpatterns = [
    path('test', views_user.test),
    path('update/<str:user_id>', views_user.update_user),
    path('delete/<str:user_id>', views_user.delete_user),
    path('signout', views_user.signout),
    path('getusers', views_user.get_users),
    path('<str:user_id>', views_user.get_user),
]
