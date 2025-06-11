from rest_framework.viewsets import ModelViewSet
from rest_framework import status
from rest_framework.response import Response
from django.http import FileResponse, HttpResponseForbidden
from .models import File
from .serializers import FileSerializer, ConvertSerializer
from utils.utils import CSVSplitter, uploading_to_supabase, create_bucket
from rest_framework.parsers import MultiPartParser
import os
from django.conf import settings
from uuid import uuid4
import requests
from rest_framework.decorators import action, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from utils.utils import supabase, uploading_to_supabase, remove_files
from utils.throttles import FileProcessingAnonThrottle, FileProcessingUserThrottle


class FileViewSet(ModelViewSet):
    queryset = File.objects.all()
    serializer_class = FileSerializer
    parser_classes = [MultiPartParser]
    throttle_classes = [FileProcessingUserThrottle, FileProcessingAnonThrottle]
    
    
    def get_queryset(self):
        if self.request.user.is_authenticated:
            return self.queryset.filter(user=self.request.user)
        return self.queryset.filter(user=None)
    
    def get_permissions(self):
        if self.action not in ['create']:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
            
    
    @action(detail=False, methods=['post'], url_path='split-csv')
    def split_csv(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        file = request.data.get('file')
        base_name = f"{(file.name).split('.')[0]}"
        lines_per_file = request.data.get('lines_per_file')
        size_per_file = request.data.get('size_per_file')
        upload_dir = os.path.join(settings.MEDIA_ROOT, 'chunks')
        os.makedirs(upload_dir, exist_ok=True)
        if not file:
            return Response({'error': "file not found"}, status=status.HTTP_400_BAD_REQUEST)
        if not lines_per_file and not size_per_file:
            return Response({'error': 'You must provide at least one way to split - by lines or size(mb)'})
        if lines_per_file and size_per_file:
            return Response({'error': 'Provide only one of lines_per_file or size_per_file, not both'})
        try:
            local_path = os.path.join(upload_dir, file.name)
            bucket_name = 'chunkfiles'
            create_bucket(bucket_name)
            with open(local_path, "wb+") as f:
                for chunk in file.chunks():
                    f.write(chunk)
            split_instance = CSVSplitter(local_path)
            if lines_per_file:
                zip_path = split_instance.split_by_lines(int(lines_per_file))
            else:
                zip_path = split_instance.split_by_size(int(size_per_file))
            supabase_path = f"{str(uuid4())}/{base_name}.zip"
            print(f"Zip path: {zip_path}")
            os.remove(local_path)
            with open(zip_path, "rb") as f:
                try:
                    print("Uploading to supabase")
                    uploading_to_supabase(bucket_name, f, supabase_path)
                    print("Upload complete")
                    os.remove(zip_path)
                    print(supabase_path)
                except Exception as e:
                    return Response({'error uploading file': str(e)}, status=status.HTTP_400_BAD_REQUEST)
                
            signed_url = supabase.storage.from_(bucket_name).create_signed_url(supabase_path, 3600)["signedURL"]
            serializer.save(user=request.user if request.user.is_authenticated else None, file=file.name, zipped_file_path=supabase_path, bucket_name=bucket_name, operation='split')
            return Response({"download-url": signed_url}, status=status.HTTP_200_OK)
        
        #####  Commented out FileResposne
        #    r = requests.get(signed_url, stream=True)
        #    return FileResponse(r.raw, as_attachment=True, filename=f"{base_name}.zip")
        except Exception as e:
            print(str(e))
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
    @action(detail=False, methods=['post'], url_path='convert-csv', serializer_class=ConvertSerializer)
    def convert_csv(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        file = request.data.get('file')
        base_name = (file.name).split(".")[0]
        output_dir = os.path.join(settings.MEDIA_ROOT, 'convert', str(uuid4()))
        os.makedirs(output_dir, exist_ok=True)
        local_path = os.path.join(output_dir, file.name)
        with open(local_path, 'wb+') as f:
            for chunk in file.chunks():
                f.write(chunk)
                
        try:
            convert_instance = CSVSplitter(local_path)
            json_path = convert_instance.convert_csv_to_json(output_dir)
            print(f"FIle Converted Successfully - JSON Path: {json_path}")
            os.remove(local_path)
            supabase_path = f"{str(uuid4())}/{base_name}.zip"
            bucket_name = "convert-files"
            create_bucket(bucket_name)
            print("Bucket created")
            with open(json_path, "rb") as f:
                try:
                    print("uploading file to supabase")
                    uploading_to_supabase(bucket_name, f, supabase_path)
                    print("Upload successful")
                    os.remove(json_path)
                except Exception as e:
                    return Response({'error uploading to storage bucket': str(e)}, status=status.HTTP_400_BAD_REQUEST)
                
            signed_url = supabase.storage.from_(bucket_name).create_signed_url(supabase_path, 3600)["signedURL"]
            #save information to db
            serializer.save(user=request.user if request.user.is_authenticated else None, file=file.name, zipped_file_path=supabase_path, bucket_name=bucket_name, operation='convert')
            return Response({"download-url": signed_url}, status=status.HTTP_200_OK)
            #Commented out FileResponse
            # r = requests.get(signed_url, stream=True)
            #return FileResponse(r.raw, as_attachment=True, filename=f"{base_name}.zip")
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
    
    @action(methods=['get'], detail=True, url_path='download-file', permission_classes=[IsAuthenticated])
    def download_file(self, request, pk):
        file = self.queryset.get(id=pk)
        if not file:
            return Response({'not_found': "The requested resource was not found"}, status= status.HTTP_404_NOT_FOUND)
        supabase_path = file.zipped_file_path
        filename = str(file.file).split('.')[0]
        bucket_name = file.bucket_name
        signed_url = supabase.storage.from_(bucket_name).create_signed_url(supabase_path, 3600)['signedURL']
        r = requests.get(signed_url, stream=True)
        return FileResponse(r.raw, as_attachment=True, filename=f"{filename}.zip")
    
    @action(methods=['get'], url_path='cleanup-files', detail=False)
    def clean_supabase_buckets(self, request):
        if request.headers.get("X-Cron-Token") != os.getenv("CRON_SECRET_TOKEN"):
            return HttpResponseForbidden("Forbidden")
        remove_files()
        return Response({"success": "Files cleaned successfully"}, status=status.HTTP_200_OK)