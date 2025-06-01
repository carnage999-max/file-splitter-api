from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FileViewSet

router = DefaultRouter()

router.register('split-csv', FileViewSet, basename='split_csv')

urlpatterns = [
    path('', include(router.urls))
]

