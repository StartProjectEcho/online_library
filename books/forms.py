# books/forms.py
from django import forms
from django.core.exceptions import ValidationError

from .models import Book, Author, Genre


class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = [
            'title',
            'author',
            'genres',
            'description',
            'publication_year',
            'isbn',
            'age_rating',
            'image',
            'epigraph'
        ]
        widgets = {
            'genres': forms.SelectMultiple(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'rows': 4}),
            'epigraph': forms.Textarea(attrs={'rows': 2}),
        }

    def clean_title(self):
        title = self.cleaned_data['title']
        if Book.objects.filter(title=title).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("Книга с таким названием уже существует.")
        return title

    def clean_isbn(self):
        isbn = self.cleaned_data['isbn']
        if Book.objects.filter(isbn=isbn).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("Книга с таким ISBN уже существует.")
        return isbn



class AuthorForm(forms.ModelForm):
    class Meta:
        model = Author
        fields = ['name', 'biography']

    def clean_name(self):
        name = self.cleaned_data['name']
        # Получаем текущего автора (если редактируем)
        current_author = self.instance

        # Проверяем, есть ли автор с таким именем
        if Author.objects.filter(name__iexact=name).exclude(
                id=current_author.id).exists():  # Если это создание нового автора и такой уже есть
            if not current_author.id:
                raise ValidationError("Автор с таким именем уже существует.")
            # Если это редактирование, но имя не менялось
            elif current_author.name == name:
                return name
            else:
                raise ValidationError("Автор с таким именем уже существует.")
        return name


class GenreForm(forms.ModelForm):
    class Meta:
        model = Genre
        fields = ['name']

    def clean_name(self):
        name = self.cleaned_data['name']
        current_genre = self.instance

        if Genre.objects.filter(name=name).exists():
            # Если это создание нового жанра и такой уже есть
            if not current_genre.id:
                raise forms.ValidationError("Жанр с таким именем уже существует.")
            # Если это редактирование и имя не изменилось
            elif current_genre.name == name:
                return name
            else:
                raise forms.ValidationError("Жанр с таким именем уже существует.")

        return name
