"""
URL configuration for file_slicer project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseForbidden


def index(request):
    return render(request, 'index.html')

def ping_site(request):
    if request.headers.get("X-Cron-Token") != os.getenv("CRON_SECRET_TOKEN"):
            return HttpResponseForbidden("Forbidden")
    return HttpResponse("Hello World")

urlpatterns = [
    path("", index, name="index"),
    path('admin/', admin.site.urls),
    path('files/', include("splitfile.urls")),
    path('users/', include("users.urls")),
    path('ping/', ping_site, name='ping'),
    
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]
