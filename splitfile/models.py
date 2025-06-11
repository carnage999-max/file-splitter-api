from django.db import models
from uuid import uuid4
from django.utils.translation import gettext_lazy as _


class File(models.Model):
    id = models.UUIDField(_("File UUID"), primary_key=True, unique=True, db_index=True, default=uuid4(), auto_created=True)
    user = models.ForeignKey("users.CustomUser", on_delete=models.CASCADE, null=True, blank=True)
    file = models.FileField(_("File"), blank=False, null=False, upload_to='uploaded_files/public/')
    zipped_file_path = models.CharField(_("Zip Path on Supabase"), max_length=1024, null=True, blank=True)
    lines_per_file = models.IntegerField(_("Number of lines per file"), null=True, blank=True)
    size_per_file = models.IntegerField(_("Size Per File(Mb)"), null=True, blank=True)
    bucket_name = models.CharField(_("Storage Bucket"), max_length=1024, default='chunkfiles')
    operation = models.CharField(_("Operation done on file"), max_length=200)
    created_at = models.DateTimeField(_("Time of split"), auto_now_add=True)
    
    def __str__(self) -> str:
        return str(self.id)
