from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from library_project.views import HomePageView
from stats.views import DashboardView
from users.views import NoPermissionView, ProfileView

urlpatterns = [
    path('profile/', ProfileView.as_view(), name='profile'),
    path('admin/', admin.site.urls),
    path('users/', include('users.urls')),
    path('books/', include('books.urls')),
    path('news/', include('news.urls')),
    path('reviews/', include('reviews.urls')),
    path('', HomePageView.as_view(), name='home'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('recommendations/', include('recommendations.urls')),
    path('no-permission/', NoPermissionView.as_view(), name='no_permission'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
