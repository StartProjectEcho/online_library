# books/models.py
import os

from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.db.models import Avg
from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy


class Author(models.Model):
    name = models.CharField(max_length=100, unique=True)
    biography = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class Genre(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Book(models.Model):
    AGE_RATINGS = [
        ('0+', '0+'),
        ('6+', '6+'),
        ('12+', '12+'),
        ('16+', '16+'),
        ('18+', '18+'),
    ]

    title = models.CharField(max_length=200, unique=True)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    genres = models.ManyToManyField('Genre', blank=True)
    description = models.TextField(blank=True, null=True)
    publication_year = models.PositiveIntegerField()
    isbn = models.CharField(max_length=13, unique=True)
    age_rating = models.CharField(max_length=3, choices=AGE_RATINGS, default='12+')
    image = models.ImageField(
        upload_to='book_covers/',
        blank=True,
        null=True,
        default='book_covers/standart_foto.png'
    )
    epigraph = models.TextField(blank=True, null=True)
    added_at = models.DateTimeField(auto_now_add=True)

    def get_image_url(self):
        if self.image and hasattr(self.image, 'url'):
            return self.image.url
        return '/media/book_covers/standart_foto.png'

    def save(self, *args, **kwargs):
        if self.pk:
            orig = Book.objects.get(pk=self.pk)
            if orig.image and orig.image != self.image:
                if os.path.isfile(orig.image.path):
                    os.remove(orig.image.path)
        super().save(*args, **kwargs)

    def get_average_rating(self):
        avg = self.reviews.aggregate(rating_avg=Avg('rating'))['rating_avg']
        return round(avg, 1) if avg else 0

    class Meta:
        indexes = [
            models.Index(fields=['publication_year']),
            models.Index(fields=['title']),
        ]

    def __str__(self):
        return self.title

@receiver(post_delete, sender=Book)
def delete_book_cover_on_delete(sender, instance, **kwargs):
    if instance.image and os.path.isfile(instance.image.path):
        os.remove(instance.image.path)

    def __str__(self):
        return self.title


# books/models.py

class BookStatus(models.Model):
    STATUS_CHOICES = [
        ('read', 'Прочитано'),
        ('planned', 'В планах'),
        ('favorite', 'Любимое'),
        ('abandoned', 'Заброшено'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)

    def __str__(self):
        return f"{self.user.username} — {self.get_status_display()} — {self.book.title}"

    class Meta:
        unique_together = ('user', 'book')

