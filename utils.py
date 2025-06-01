import csv
import os
from uuid import uuid4
import shutil

class CSVSplitter:
    def __init__(self, input_file):
        self.input_file = input_file
        self.header = None

    def _read_header(self):
        with open(self.input_file, 'r', newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            self.header = next(reader)
    
    def create_folder(self):
        folder_name = str(uuid4())
        os.makedirs(folder_name)
        return folder_name
    
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
            if not str(file).endswith('zip'):
                os.remove(file)
        

    def split_by_lines(self, lines_per_file):
        self._read_header()
        part = 1
        output_files = []
        name = " "
        output_name = lambda p: f"{name}_{p}.csv"

        with open(self.input_file, 'r', newline='', encoding='utf-8') as f:
            name = f.name.split(".")[0]
            reader = csv.reader(f)
            next(reader)  # skip header again

            rows = []
            folder = self.create_folder()
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
            
        self.compress_folder_to_zip(folder, os.path.join(folder, name))
        self.remove_files(folder)
        return output_files

    def split_by_size(self, max_size_mb):
        self._read_header()
        max_bytes = max_size_mb * 1024 * 1024
        part = 1
        output_files = []
        name = ""
        output_name = lambda p: f"{name}_{p}.csv"

        with open(self.input_file, 'r', newline='', encoding='utf-8') as f:
            name = f.name.split(".")[0]
            reader = csv.reader(f)
            next(reader)  # skip header again
            folder = self.create_folder()
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
                    
                    file_name = os.path.join(folder, f"{name}_{part}.csv")
                    out = open(file_name, 'w', newline='', encoding='utf-8')
                    writer = csv.writer(out)
                    writer.writerow(self.header)

            out.close()
            output_files.append(file_name)
        self.compress_folder_to_zip(folder, os.path.join(folder, name))
        self.remove_files(folder)
        return output_files