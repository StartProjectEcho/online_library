from django.contrib import admin
from .models import Book, Author, Genre

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'publication_year', 'age_rating']
    filter_horizontal = ['genres']
    fields = ['title', 'author', 'description', 'publication_year', 'isbn', 'age_rating', 'image', 'epigraph', 'genres']

admin.site.register(Author)
admin.site.register(Genre)