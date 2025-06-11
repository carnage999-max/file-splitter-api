import csv
from datetime import timedelta
import os
import json
from uuid import uuid4
import shutil
from django.conf import settings
import zipfile
from dotenv import load_dotenv
from supabase import create_client, Client
from storage3.exceptions import StorageApiError
from django.utils import timezone
from splitfile.models import File

load_dotenv()

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

class CSVSplitter:
    def __init__(self, input_file):
        self.input_file = input_file
        self.header = None

    def _read_header(self):
        with open(self.input_file, 'r', newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            self.header = next(reader)
    
    def create_folder(self, base_path="."):
        folder_name = str(uuid4())
        full_path = os.path.join(base_path, folder_name)
        os.makedirs(full_path, exist_ok=True)
        print(f"Full UUID path: {full_path}")
        return full_path
    
    def compress_folder_to_zip(self, source_folder, zip_output_path):
        """
        Compresses the contents of a folder into a .zip file.
        
        Args:
            source_folder (str): Path to the folder to zip.
            zip_output_path (str): Full path to the resulting zip file (without .zip extension).
        """
        if not os.path.isdir(source_folder):
            raise ValueError("Source must be a directory.")

        # Make archive (will create zip at zip_output_path.zip)
        shutil.make_archive(zip_output_path, 'zip', root_dir=source_folder)
        return f"{zip_output_path}.zip"
    
    def get_all_file_paths(self, directory):
        file_paths = []

        for root, directories, files in os.walk(directory):
            for filename in files:
                file_path = os.path.join(root, filename)
                file_paths.append(file_path)
        return file_paths
    
    def remove_files(self, path):
        for file in self.get_all_file_paths(path):
            os.remove(file)
        

    def split_by_lines(self, lines_per_file):
        self._read_header()
        part = 1
        output_files = []

        with open(self.input_file, 'r', newline='', encoding='utf-8') as f:
            base_name = os.path.splitext(os.path.basename(f.name))[0]
            output_name = lambda p: f"{base_name}_{p}.csv"
            reader = csv.reader(f)
            next(reader)  # skip header again

            rows = []
            folder = self.create_folder(base_path=os.path.join(settings.MEDIA_ROOT, "chunks"))
            print(f"Folder containing chunks: {folder}")
            for i, row in enumerate(reader, 1):
                rows.append(row)
                if i % lines_per_file == 0:
                    file_name = os.path.join(folder, output_name(part))
                    print(file_name)
                    with open(file_name, 'w', newline='', encoding='utf-8') as out:
                        writer = csv.writer(out)
                        writer.writerow(self.header)
                        writer.writerows(rows)
                    output_files.append(file_name)
                    rows = []
                    part += 1

            if rows:
                file_name = os.path.join(folder, output_name(part))
                with open(file_name, 'w', newline='', encoding='utf-8') as out:
                    writer = csv.writer(out)
                    writer.writerow(self.header)
                    writer.writerows(rows)
                output_files.append(file_name)
        print(f"Output Files::  {output_files}")
        parent = os.path.dirname(folder)
        zip_path_ = os.path.join(parent, f"{base_name}")
        zip_path = self.compress_folder_to_zip(folder, zip_path_)
        self.remove_files(folder)
        os.rmdir(folder)
        return zip_path

    def split_by_size(self, max_size_mb):
        self._read_header()
        max_bytes = max_size_mb * 1024 * 1024
        part = 1
        output_files = []

        with open(self.input_file, 'r', newline='', encoding='utf-8') as f:
            base_name = os.path.splitext(os.path.basename(f.name))[0]
            output_name = lambda p: f"{base_name}_{p}.csv"
            # name = f.name.split(".")[0]
            reader = csv.reader(f)
            next(reader)  # skip header again
            folder = self.create_folder(base_path=os.path.join(settings.MEDIA_ROOT, "chunks"))
            file_name = os.path.join(folder, output_name(part))
            out = open(file_name, 'w', newline='', encoding='utf-8')
            writer = csv.writer(out)
            writer.writerow(self.header)

            for row in reader:
                writer.writerow(row)
                out.flush()
                
                if out.tell() >= max_bytes:
                    out.close()
                    output_files.append(file_name)
                    part += 1
                    
                    file_name = os.path.join(folder, f"{base_name}_{part}.csv")
                    out = open(file_name, 'w', newline='', encoding='utf-8')
                    writer = csv.writer(out)
                    writer.writerow(self.header)

            out.close()
            output_files.append(file_name)
        print(f"Output Files::  {output_files}")
        parent = os.path.dirname(folder)
        zip_path_ = os.path.join(parent, f"{base_name}")
        zip_path = self.compress_folder_to_zip(folder, zip_path_)
        self.remove_files(folder)
        os.rmdir(folder)
        return zip_path
    
    
    def convert_csv_to_json(self, output_dir=None):
        if output_dir is None:
            output_dir = os.path.dirname(self.input_file)
        json_file_name = os.path.splitext(os.path.join(self.input_file))[0] + '.json'
        json_path =  os.path.join(output_dir, json_file_name)
            
        with open(self.input_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            data = list(reader)
            
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        output_zip_path = os.path.join(output_dir, f"{(json_file_name).split('.')[0]}.zip")
        try:
            with zipfile.ZipFile(output_zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                zipf.write(json_path, arcname=os.path.basename(json_path))
            print(f"File '{json_path}' compressed successfully to '{output_dir}'")
            os.remove(json_path)
        except Exception as e:
            print(f"An error occurred: {e}")
        return output_zip_path
    
    
    
    
def create_bucket(bucket_name):
    try:
        response = supabase.storage.get_bucket(bucket_name)
    except StorageApiError:
        response = supabase.storage.create_bucket(
                    bucket_name,
                    options={
                        "public": False,
                    }
                )
    return response

def uploading_to_supabase(bucket_name, file, path):
    supabase.storage.from_(bucket_name).upload(
                        file=file,
                        path=path,
                        file_options={"cache-control": "3600", "upsert": "false"}
                    )
    
def remove_files():
    dead_time = timezone.now() - timedelta(days=3)
    files = File.objects.filter(created_at__lt=dead_time)
    for file in files:
        try:
            supabase.storage.from_(file.bucket_name).remove([file.zipped_file_path])
        except Exception:
            pass