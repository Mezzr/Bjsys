from django.shortcuts import render
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView
# Create your views here.

class MeView(APIView):
    """获取当前登录用户信息的视图"""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        user_data = {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "site": user.site.name if user.site else None,
            "site_id": user.site.id if user.site else None,
            "can_edit_own_site": user.can_edit_own_site,
            "can_view_all_sites": user.can_view_all_sites,
            "can_manage_users": user.can_manage_users,
            
        }
        return Response(user_data)

class LogoutView(APIView):
    """用户登出视图"""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        # 对于 JWT，服务器端通常不需要做太多操作，
        # 除非实现了 token 黑名单 (blacklist)。
        # 这里简单返回成功响应，由前端清除 token。
        return Response({"message": "Successfully logged out"}, status=200)
