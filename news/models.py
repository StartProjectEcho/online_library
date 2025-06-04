# news/models.py

from django.db import models
from django.utils import timezone

class Post(models.Model):
    title = models.CharField('Заголовок', max_length=200, unique=True)
    subtitle = models.CharField('Подзаголовок', max_length=255, blank=True, null=True)
    content = models.TextField('Описание')
    published_at = models.DateTimeField('Дата публикации', default=timezone.now)

    def __str__(self):
        return self.title