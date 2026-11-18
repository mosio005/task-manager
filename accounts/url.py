from django.urls import path
from .views import RegisterView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView



urlpatterns = [
    path(
        'token/', 
        TokenObtainPairView.as_view(), 
        name='token-obtain-pair'
    ),

    path(
        'token/refresh/',
        TokenRefreshView.as_view(),
        name='refresh-token'
    ),


    path(
        'register/',
        RegisterView.as_view(),
        name='register'
    ),
]