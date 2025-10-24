from django.urls import path, include

from .views import  StringAnalyzerViewSet
from rest_framework.routers import  DefaultRouter

router = DefaultRouter(trailing_slash=False)
router.register(r'strings', StringAnalyzerViewSet, basename='strings')

urlpatterns = [
    path('', include(router.urls)),
]