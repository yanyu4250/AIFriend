import uuid

from django.db import models
from django.utils.timezone import now, localtime
from web.models.user import UserProfile


def document_upload_to(instance, filename):
    ext = filename.split('.')[-1]
    filename = f'{uuid.uuid4().hex[:10]}.{ext}'
    return f'knowledge/documents/{instance.user.user_id}_{filename}'


class KnowledgeDocument(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    filename = models.CharField(max_length=255)
    file_type = models.CharField(max_length=20)
    file = models.FileField(upload_to=document_upload_to)
    file_size = models.IntegerField(default=0)
    chunk_count = models.IntegerField(default=0)
    status = models.CharField(max_length=20, default='processing')
    error_message = models.TextField(blank=True, default='')
    create_time = models.DateTimeField(default=now)

    def __str__(self):
        return f"{self.user.user.username} - {self.filename} - {localtime(self.create_time).strftime('%Y-%m-%d %H:%M:%S')}"


class KnowledgeChunk(models.Model):
    document = models.ForeignKey(KnowledgeDocument, on_delete=models.CASCADE, related_name='chunks')
    chunk_index = models.IntegerField()
    content = models.TextField()
    create_time = models.DateTimeField(default=now)

    def __str__(self):
        return f"{self.document.filename} - chunk {self.chunk_index}"
