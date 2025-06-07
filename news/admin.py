# news/admin.py

from django.contrib import admin
from .models import Post

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['title', 'published_at']
    prepopulated_fields = {'subtitle': ('title',)}  # Опционально