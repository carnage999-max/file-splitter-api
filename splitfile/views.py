from rest_framework.viewsets import ModelViewSet
from rest_framework import status
from rest_framework.response import Response
from django.http import FileResponse
from .models import File
from .serializers import FileSerializer


class FileViewSet(ModelViewSet):
    queryset = File.objects.all()
    http_method_names = ['post']
    serializer_class = FileSerializer
    
    
    def get_serializer()
