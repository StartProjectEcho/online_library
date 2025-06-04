from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy, reverse
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from .models import Review
from .forms import ReviewForm

class ReviewCreateView(CreateView):
    model = Review
    form_class = ReviewForm
    template_name = 'reviews/review_form.html'

    def form_valid(self, form):
        book_id = self.kwargs.get('book_id')
        form.instance.book_id = book_id
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        book_id = self.kwargs.get('book_id')
        return reverse_lazy('book-detail', kwargs={'pk': book_id})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['book_id'] = self.kwargs.get('book_id')
        return context

class ReviewUpdateView(UpdateView):
    model = Review
    form_class = ReviewForm
    template_name = 'reviews/review_form.html'

    def get_object(self, queryset=None):
        # Гарантируем загрузку объекта через URL-параметр 'pk'
        return get_object_or_404(Review, pk=self.kwargs.get('pk'))

    def get_success_url(self):
        # Используем book_id из объекта отзыва
        return reverse('book-detail', kwargs={'pk': self.object.book.id})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Используем существующий объект отзыва
        context['book_id'] = self.object.book.id
        return context

class ReviewDeleteView(LoginRequiredMixin, DeleteView):
    model = Review
    template_name = 'reviews/review_confirm_delete.html'

    def get_object(self, queryset=None):
        # Гарантируем загрузку объекта через URL-параметр 'pk'
        return get_object_or_404(Review, pk=self.kwargs.get('pk'))

    def get_success_url(self):
        return reverse('book-detail', kwargs={'pk': self.object.book.id})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Используем существующий объект отзыва
        context['book_id'] = self.object.book.id
        return context