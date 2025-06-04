from django.db.models import Count
from django.views.generic import TemplateView
from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import redirect
from books.models import Book
from users.models import CustomUser


class DashboardView(UserPassesTestMixin, TemplateView):
    template_name = 'dashboard.html'

    def test_func(self):
        return self.request.user.groups.filter(name='Библиотекарь').exists()

    def handle_no_permission(self):
        return redirect('no_permission')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Получаем GET-параметры
        selected_year = self.request.GET.get('year')
        selected_rating = self.request.GET.get('rating')

        # Фильтруем книги
        books = Book.objects.all()

        # Обработка фильтра по году
        context['selected_year'] = None
        if selected_year and selected_year != '':
            try:
                # Преобразуем в целое число для фильтрации
                year_int = int(selected_year)
                books = books.filter(publication_year=year_int)
                context['selected_year'] = year_int  # Сохраняем как число
            except (TypeError, ValueError):
                # Если преобразование не удалось, игнорируем фильтр
                pass

        # Обработка фильтра по возрастному рейтингу
        context['selected_rating'] = None
        if selected_rating and selected_rating != '':
            books = books.filter(age_rating=selected_rating)
            context['selected_rating'] = selected_rating

        # Годы для выпадающего списка (уникальные, отсортированные по убыванию)
        all_years = Book.objects.values_list('publication_year', flat=True) \
            .distinct() \
            .order_by('-publication_year')
        context['all_years'] = list(all_years)  # Оставляем как числа

        # Возрастные рейтинги
        context['age_ratings'] = Book.AGE_RATINGS

        # Книги по годам
        yearly_books = books.values('publication_year') \
            .annotate(count=Count('id')) \
            .order_by('publication_year')
        context['yearly_books'] = list(yearly_books)

        # Книги по жанрам (топ-10)
        genre_books = books.values('genres__name') \
                          .annotate(count=Count('id')) \
                          .order_by('-count')[:10]
        context['genre_books'] = list(genre_books)

        # Распределение по возрастному рейтингу
        rating_books = books.values('age_rating') \
            .annotate(count=Count('id')) \
            .order_by('-count')
        context['rating_books'] = list(rating_books)

        # Общая статистика
        context['total_books'] = books.count()
        context['total_users'] = CustomUser.objects.count()
        context['total_authors'] = books.values('author').distinct().count()

        return context