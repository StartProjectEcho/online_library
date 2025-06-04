# books/views.py
import os
from datetime import datetime
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
    FormView
)
from django.contrib.auth.mixins import UserPassesTestMixin
from .models import Book, Genre, Author, BookStatus
from .forms import BookForm, AuthorForm, GenreForm


# === Список книг ===
class BookListView(ListView):
    model = Book
    template_name = 'books/book_list.html'
    context_object_name = 'books'
    paginate_by = 12

    def get_queryset(self):
        queryset = super().get_queryset().select_related('author').prefetch_related('genres')

        # Получаем параметры фильтрации
        status = self.request.GET.get('status')
        genre_ids = self.request.GET.getlist('genres')
        author_id = self.request.GET.get('author')
        rating = self.request.GET.get('rating')
        year = self.request.GET.get('year')
        title = self.request.GET.get('title', '').strip()
        isbn = self.request.GET.get('isbn', '').strip()

        # Фильтрация по статусу (только для авторизованных пользователей)
        if status and self.request.user.is_authenticated:
            queryset = queryset.filter(
                bookstatus__user=self.request.user,
                bookstatus__status=status
            )

        if isbn:
            queryset = queryset.filter(isbn__icontains=isbn)
        if author_id:
            queryset = queryset.filter(author_id=author_id)
        if year:
            queryset = queryset.filter(publication_year=year)
        if rating:
            queryset = queryset.filter(age_rating=rating)
        if title:
            queryset = queryset.filter(title__icontains=title)

        if genre_ids:
            genre_ids = [int(g) for g in genre_ids]
            queryset = queryset.annotate(
                matched_genres=Count('genres', filter=Q(genres__id__in=genre_ids))
            ).filter(matched_genres=len(genre_ids)).distinct()

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['genres'] = Genre.objects.all()
        context['authors_list'] = Author.objects.all().order_by('name')
        context['selected_genres'] = [int(g) for g in self.request.GET.getlist('genres')] if self.request.GET.getlist(
            'genres') else []
        context['age_ratings'] = Book.AGE_RATINGS
        context['is_paginated'] = context['page_obj'].has_other_pages()
        context['current_year'] = datetime.now().year

        # Добавляем статусы в контекст
        context['status_choices'] = BookStatus.STATUS_CHOICES

        # Получаем статусы книг для текущего пользователя
        user = self.request.user
        if user.is_authenticated:
            book_ids = context['books'].values_list('id', flat=True)
            statuses = BookStatus.objects.filter(user=user, book_id__in=book_ids)
            context['books_with_status'] = {
                bs.book_id: bs.status for bs in statuses
            }
        else:
            context['books_with_status'] = {}

        return context



from .models import BookStatus


class BookDetailView(DetailView):
    model = Book
    template_name = 'books/book_detail.html'
    context_object_name = 'book'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        all_reviews = self.object.reviews.all().order_by('-created_at')

        # Пагинация отзывов
        paginator = Paginator(all_reviews, 1)
        page_number = self.request.GET.get('page')
        context['page_obj'] = paginator.get_page(page_number)
        context['is_paginated'] = paginator.num_pages > 1

        # Безопасное получение статуса и отзыва пользователя
        if self.request.user.is_authenticated:
            context['user_status'] = BookStatus.objects.filter(
                user=self.request.user,
                book=self.object
            ).first()
            context['user_review'] = all_reviews.filter(
                user=self.request.user
            ).first()
        else:
            context['user_status'] = None
            context['user_review'] = None

        context['status_choices'] = BookStatus.STATUS_CHOICES
        return context


from django.views.generic.edit import FormView
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404

class UpdateBookStatusView(FormView):
    template_name = 'books/book_detail.html'
    success_url = reverse_lazy('book-list')

    def post(self, request, *args, **kwargs):
        book = get_object_or_404(Book, id=kwargs['book_id'])
        status = request.POST.get('status')
        remove = request.POST.get('remove')

        if remove:
            BookStatus.objects.filter(user=request.user, book=book).delete()
        elif status:
            BookStatus.objects.update_or_create(
                user=request.user,
                book=book,
                defaults={'status': status}
            )

        return redirect('book-detail', pk=book.id)


# === Добавление книги ===
class BookCreateView(UserPassesTestMixin, CreateView):
    model = Book
    form_class = BookForm
    template_name = 'books/book_form.html'
    success_url = reverse_lazy('book-list')

    def test_func(self):
        return self.request.user.groups.filter(name='Библиотекарь').exists()

    def handle_no_permission(self):
        return redirect('no_permission')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Добавить книгу'
        return context

    def form_valid(self, form):
        # Удаляем старую обложку, если она была заменена
        if self.object.image and 'image' in form.changed_data:
            old_image_path = self.object.image.path
            if os.path.isfile(old_image_path):
                os.remove(old_image_path)
        return super().form_valid(form)


# === Редактирование книги ===
class BookUpdateView(UserPassesTestMixin, UpdateView):
    model = Book
    form_class = BookForm
    template_name = 'books/book_form.html'
    success_url = reverse_lazy('book-list')

    def test_func(self):
        return self.request.user.groups.filter(name='Библиотекарь').exists()

    def handle_no_permission(self):
        return redirect('no_permission')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Редактировать книгу'
        return context

    def form_valid(self, form):
        if self.object.image and 'image' in form.changed_data:
            old_image_path = self.object.image.path
            if os.path.isfile(old_image_path):
                os.remove(old_image_path)
        return super().form_valid(form)


# === Удаление книги ===
class BookDeleteView(UserPassesTestMixin, DeleteView):
    model = Book
    template_name = 'books/book_confirm_delete.html'
    success_url = reverse_lazy('book-list')

    def test_func(self):
        return self.request.user.groups.filter(name='Библиотекарь').exists()

    def handle_no_permission(self):
        return redirect('no_permission')


# === Список авторов ===
class AuthorListView(ListView):
    model = Author
    template_name = 'books/author_list.html'
    context_object_name = 'authors'
    paginate_by = 12

    def get_queryset(self):
        queryset = super().get_queryset()
        q = self.request.GET.get('q')
        if q:
            queryset = queryset.filter(name__icontains=q)
        queryset = queryset.annotate(book_count=Count('book'))
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('q', '')
        context['is_paginated'] = context['page_obj'].has_other_pages()
        return context


# === Детали автора ===
class AuthorDetailView(DetailView):
    model = Author
    template_name = 'books/author_detail.html'
    context_object_name = 'author'


# === Добавление автора ===
class AuthorCreateView(UserPassesTestMixin, CreateView):
    model = Author
    form_class = AuthorForm
    template_name = 'books/author_form.html'
    success_url = reverse_lazy('author-list')

    def test_func(self):
        return self.request.user.groups.filter(name='Библиотекарь').exists()

    def handle_no_permission(self):
        return redirect('no_permission')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Добавить автора'
        return context


# === Редактирование автора ===
class AuthorUpdateView(UserPassesTestMixin, UpdateView):
    model = Author
    form_class = AuthorForm
    template_name = 'books/author_form.html'
    success_url = reverse_lazy('author-list')

    def test_func(self):
        return self.request.user.groups.filter(name='Библиотекарь').exists()

    def handle_no_permission(self):
        return redirect('no_permission')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Редактировать автора'
        return context


# === Удаление автора ===
class AuthorDeleteView(UserPassesTestMixin, DeleteView):
    model = Author
    template_name = 'books/author_confirm_delete.html'
    success_url = reverse_lazy('author-list')

    def test_func(self):
        return self.request.user.groups.filter(name='Библиотекарь').exists()

    def handle_no_permission(self):
        return redirect('no_permission')


# === Список жанров ===
class GenreListView(ListView):
    model = Genre
    template_name = 'books/genre_list.html'
    context_object_name = 'genres'
    paginate_by = 12

    def get_queryset(self):
        queryset = super().get_queryset()
        q = self.request.GET.get('q')
        if q:
            queryset = queryset.filter(name__icontains=q)
        queryset = queryset.annotate(book_count=Count('book'))
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('q', '')
        context['is_paginated'] = context['page_obj'].has_other_pages()
        return context


# === Детали жанра ===
class GenreDetailView(DetailView):
    model = Genre
    template_name = 'books/genre_detail.html'
    context_object_name = 'genre'


# === Добавление жанра ===
class GenreCreateView(UserPassesTestMixin, CreateView):
    model = Genre
    form_class = GenreForm
    template_name = 'books/genre_form.html'
    success_url = reverse_lazy('genre-list')

    def test_func(self):
        return self.request.user.groups.filter(name='Библиотекарь').exists()

    def handle_no_permission(self):
        return redirect('no_permission')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Добавить жанр'
        return context


# === Редактирование жанра ===
class GenreUpdateView(UserPassesTestMixin, UpdateView):
    model = Genre
    form_class = GenreForm
    template_name = 'books/genre_form.html'
    success_url = reverse_lazy('genre-list')

    def test_func(self):
        return self.request.user.groups.filter(name='Библиотекарь').exists()

    def handle_no_permission(self):
        return redirect('no_permission')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Редактировать жанр'
        return context


# === Удаление жанра ===
class GenreDeleteView(UserPassesTestMixin, DeleteView):
    model = Genre
    template_name = 'books/genre_confirm_delete.html'
    success_url = reverse_lazy('genre-list')

    def test_func(self):
        return self.request.user.groups.filter(name='Библиотекарь').exists()

    def handle_no_permission(self):
        return redirect('no_permission')