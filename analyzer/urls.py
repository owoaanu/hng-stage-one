from django.urls import path, include

from . import  views
from rest_framework.routers import  DefaultRouter

router = DefaultRouter(trailing_slash=False)
router.register(r'strings', views.StringAnalyzerViewSet, basename='strings')

urlpatterns = [
    path('', include(router.urls)),
    # path('strings', views.create_analyze_string, name='create-analyze-string'),
    # path('strings', views.list_strings, name='list-strings'),
    # path('strings/filter-by-natural-language', views.filter_by_natural_language, name='natural-language-filter'),
    # path('strings/<str:string_value>', views.get_string, name='get-string'),
    # path('strings/<str:string_value>', views.delete_string, name='delete-string'),
]