from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FileViewSet, ping_site

router = DefaultRouter()

router.register('', FileViewSet, basename='csv_utils')

urlpatterns = [
    path('', include(router.urls)),
    path('ping/', ping_site, name='ping')
]

