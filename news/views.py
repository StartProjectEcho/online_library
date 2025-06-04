# news/views.py
from django.shortcuts import redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.utils import timezone
from django.contrib.auth.mixins import UserPassesTestMixin
from .models import Post
from .forms import PostForm

# Представления для постов
class PostListView(ListView):
    model = Post
    template_name = 'news/post_list.html'
    context_object_name = 'posts'
    ordering = ['-published_at']
    paginate_by = 6

class PostDetailView(DetailView):
    model = Post
    template_name = 'news/post_detail.html'
    context_object_name = 'post'

class PostCreateView(UserPassesTestMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'news/post_form.html'
    success_url = reverse_lazy('post-list')

    def test_func(self):
        return self.request.user.groups.filter(name='Библиотекарь').exists()

    def handle_no_permission(self):
        return redirect('no_permission')

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        return data

    def form_valid(self, form):
        form.instance.published_at = timezone.now()
        self.object = form.save()
        return super().form_valid(form)

class PostUpdateView(UserPassesTestMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'news/post_form.html'
    success_url = reverse_lazy('post-list')

    def test_func(self):
        return self.request.user.groups.filter(name='Библиотекарь').exists()

    def handle_no_permission(self):
        return redirect('no_permission')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Редактировать новость'
        return context

    def form_valid(self, form):
        self.object = form.save()
        return super().form_valid(form)

class PostDeleteView(UserPassesTestMixin, DeleteView):
    model = Post
    template_name = 'news/post_confirm_delete.html'
    success_url = reverse_lazy('post-list')

    def test_func(self):
        return self.request.user.groups.filter(name='Библиотекарь').exists()

    def handle_no_permission(self):
        return redirect('no_permission')