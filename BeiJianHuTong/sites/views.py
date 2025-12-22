from django.shortcuts import render
from rest_framework import viewsets, permissions
from .models import Site
from .serializers import SiteSerializer

# Create your views here.

class SiteViewSet(viewsets.ReadOnlyModelViewSet):
    """场站只读接口"""
    queryset = Site.objects.all()
    serializer_class = SiteSerializer
    permission_classes = [permissions.IsAuthenticated]
