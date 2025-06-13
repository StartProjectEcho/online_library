from django.db.models import Avg
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin

from books.models import Book
from .models import RecommendedBook

class UserRecommendationsView(LoginRequiredMixin, TemplateView):
    template_name = 'recommendations/user_recommendations.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # ТОП-5 книг по рейтингу
        context['top_books'] = Book.objects.annotate(
            avg_rating=Avg('reviews__rating')
        ).order_by('-avg_rating')[:5]

        # Персонализированные рекомендации
        context['user_recs'] = RecommendedBook.objects.filter(
            user=self.request.user
        ).select_related('book').order_by('-score')[:5]

        return context