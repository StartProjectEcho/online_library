from django.core.management.base import BaseCommand
from books.models import Book, Author, Genre
from books.fixtures.test_data import AUTHORS, GENRES, BOOKS

class Command(BaseCommand):
    help = 'Загружает тестовые данные: авторы, жанры, книги'

    def handle(self, *args, **kwargs):
        # Очистка данных (не трогая пользователей и новости)
        Book.objects.all().delete()
        Genre.objects.all().delete()
        Author.objects.all().delete()

        # Загрузка жанров
        for genre_name in GENRES:
            genre, created = Genre.objects.get_or_create(name=genre_name)
            if created:
                self.stdout.write(f"✅ Жанр '{genre.name}' создан")
            else:
                self.stdout.write(f"⚠️ Жанр '{genre_name}' уже существует")

        # Загрузка авторов
        for author_data in AUTHORS:
            author, created = Author.objects.get_or_create(
                name=author_data["name"],
                defaults={"biography": author_data.get("biography", "")}
            )
            if created:
                self.stdout.write(f"✅ Автор '{author.name}' добавлен")
            else:
                self.stdout.write(f"⚠️ Автор '{author.name}' уже существует")

        # Загрузка книг
        for book_data in BOOKS:
            author = Author.objects.get(name=book_data["author"])
            book, created = Book.objects.get_or_create(
                title=book_data["title"],
                author=author,
                defaults={
                    "description": book_data.get("description", ""),
                    "publication_year": book_data["publication_year"],
                    "isbn": book_data["isbn"],
                    "age_rating": book_data["age_rating"],
                    "epigraph": book_data.get("epigraph", "")
                }
            )
            if created:
                # Добавляем жанры
                for genre_name in book_data["genres"]:
                    genre = Genre.objects.get(name=genre_name)
                    book.genres.add(genre)
                self.stdout.write(f"✅ Книга '{book.title}' добавлена")
            else:
                self.stdout.write(f"⚠️ Книга '{book.title}' уже существует")

        self.stdout.write(self.style.SUCCESS("✅ Все данные успешно загружены"))