from rest_framework.serializers import ModelSerializer
from .models import File


class FileSerializer(ModelSerializer):
    class Meta:
        model = File
        fields = '__all__'
        read_only_fields = ['id', 'zipped_file_path', 'created_at', 'bucket_name', 'user']
        
        
class ConvertSerializer(ModelSerializer):
    class Meta:
        model = File
        fields = "__all__"
        read_only_fields = ['id', 'zipped_file_path', 'created_at', 'lines_per_file', 'size_per_file', 'bucket_name', 'user']