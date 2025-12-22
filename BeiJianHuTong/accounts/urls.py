from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from . import views

urlpatterns = [
    # 登录接口 - 获取 access_token 和 refresh_token
    path("login/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    
    # 刷新令牌接口 - 用 refresh_token 获取新的 access_token
    path("refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    
    # 获取当前登录用户信息
    path("me/", views.MeView.as_view(), name="user_me"),

    # 用户登出
    path("logout/", views.LogoutView.as_view(), name="logout"),
]