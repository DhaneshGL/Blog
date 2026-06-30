from django.urls import path

from . import views_auth

urlpatterns = [
    path('signup', views_auth.signup),
    path('signin', views_auth.signin),
    path('google', views_auth.google),
]
