from django.urls import path, include
from .views import LoginUser, RegisterUser, GetUserViewSet
from rest_framework.routers import DefaultRouter


router = DefaultRouter()

router.register('login', LoginUser, basename='login')
router.register('register', RegisterUser, basename='register')
router.register('user', GetUserViewSet, basename='user')


urlpatterns = [
    path('', include(router.urls)), 
]
