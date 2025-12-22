from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'categories', views.CategoryViewSet, basename='category')
router.register(r'spare-parts', views.SparePartViewSet, basename='spare-part')
router.register(r'transactions', views.SparePartTransactionViewSet, basename='transaction')

urlpatterns = [
    path('', include(router.urls)),
]