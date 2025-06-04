# books/urls.py
from django.urls import path
from .views import BookListView, BookDetailView, BookCreateView, BookUpdateView, BookDeleteView, AuthorListView, \
    AuthorUpdateView, AuthorCreateView, AuthorDetailView, AuthorDeleteView, GenreCreateView, GenreListView, \
    GenreUpdateView, GenreDeleteView, UpdateBookStatusView

urlpatterns = [
    path('', BookListView.as_view(), name='book-list'),
    path('<int:pk>/', BookDetailView.as_view(), name='book-detail'),
    path('add/', BookCreateView.as_view(), name='book-add'),
    path('<int:pk>/edit/', BookUpdateView.as_view(), name='book-edit'),
    path('<int:pk>/delete/', BookDeleteView.as_view(), name='book-delete'),
    path('book/<int:book_id>/status/', UpdateBookStatusView.as_view(), name='update-book-status'),

    path('authors/', AuthorListView.as_view(), name='author-list'),
    path('authors/add/', AuthorCreateView.as_view(), name='author-add'),
    path('authors/<int:pk>/edit/', AuthorUpdateView.as_view(), name='author-edit'),
    path('authors/<int:pk>/', AuthorDetailView.as_view(), name='author-detail'),
    path('authors/<int:pk>/delete/', AuthorDeleteView.as_view(), name='author-delete'),

    path('genres/', GenreListView.as_view(), name='genre-list'),
    path('genres/add/', GenreCreateView.as_view(), name='genre-add'),
    path('genres/<int:pk>/edit/', GenreUpdateView.as_view(), name='genre-edit'),
    path('genres/<int:pk>/delete/', GenreDeleteView.as_view(), name='genre-delete'),
]