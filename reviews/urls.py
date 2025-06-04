
from django.urls import path
from . import views

urlpatterns = [
    path('book/<int:book_id>/review/', views.ReviewCreateView.as_view(), name='review-add'),
    path('review/<int:pk>/edit/', views.ReviewUpdateView.as_view(), name='review-edit'),
    path('review/<int:pk>/delete/', views.ReviewDeleteView.as_view(), name='review-delete'),
]