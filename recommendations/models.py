from django.db import models
from books.models import Book
from users.models import CustomUser

class RecommendedBook(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True)
    is_global = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    score = models.FloatField(default=0.0)
    class Meta:
        indexes = [
            models.Index(fields=['user', '-score']),
            models.Index(fields=['is_global', '-score']),
        ]
        verbose_name = 'Рекомендация'
        verbose_name_plural = 'Рекомендации'

    def __str__(self):
        return f"Рекомендация: {self.book.title}"