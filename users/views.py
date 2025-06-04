# users/views.py
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.urls import reverse_lazy

from books.models import BookStatus
from .forms import RegisterForm, LoginForm
from .models import CustomUser
from django.core.mail import send_mail
from django.conf import settings

from django.contrib.auth.models import Group

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()

            # Добавляем в группу "Читатель"
            try:
                reader_group = Group.objects.get(name='Читатель')
                user.groups.add(reader_group)
            except Group.DoesNotExist:
                print("Группа 'Читатель' не найдена")

            try:
                send_mail(
                    'Подтверждение email',
                    f'Перейдите по ссылке: http://localhost:8000/users/confirm/{user.id}',
                    settings.EMAIL_HOST_USER,
                    [user.email],
                    fail_silently=False
                )
                return render(request, 'users/confirmation_sent.html')
            except Exception as e:
                print("Ошибка отправки письма:", e)
                user.delete()  # Опционально: удалить пользователя при ошибке
                messages.error(request, "Не удалось отправить письмо подтверждения.")
                return redirect('register')
        else:
            messages.error(request, "Форма содержит ошибки.")
    else:
        form = RegisterForm()
    return render(request, 'registration/register.html', {'form': form})

def confirm_email(request, user_id):
    user = CustomUser.objects.get(id=user_id)
    user.is_active = True
    user.save()
    return render(request, 'users/confirmed.html')


def user_login(request):
    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')  # Убедитесь, что маршрут 'home' существует
    else:
        form = LoginForm()
    return render(request, 'registration/login.html', {'form': form})


def user_logout(request):
    logout(request)
    return redirect('login')

from django.views.generic import TemplateView

class NoPermissionView(TemplateView):
    template_name = 'no_permission.html'


class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'users/profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        # Статистика по статусам книг
        stats = {
            'favorite': BookStatus.objects.filter(user=user, status='favorite').count(),
            'planned': BookStatus.objects.filter(user=user, status='planned').count(),
            'abandoned': BookStatus.objects.filter(user=user, status='abandoned').count(),
            'read': BookStatus.objects.filter(user=user, status='read').count(),
        }

        context['stats'] = stats
        return context

from django.views.generic.edit import UpdateView
from .forms import ProfileUpdateForm

class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = CustomUser
    form_class = ProfileUpdateForm
    template_name = 'users/profile_edit.html'
    success_url = reverse_lazy('profile')

    def get_object(self):
        return self.request.user

def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    context['status_choices'] = BookStatus.STATUS_CHOICES
    return context