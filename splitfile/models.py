from django.db import models
from uuid import uuid4
from django.utils.translation import gettext_lazy as _


class File(models.Model):
    id = models.UUIDField(_("File UUID"), primary_key=True, unique=True, db_index=True, default=uuid4(), auto_created=True)
    file = models.FileField(_("File"), blank=False, null=False, upload_to='uploaded_files/public/')
    
    def __str__(self) -> str:
        return str(self.id)
