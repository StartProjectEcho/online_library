from django.urls import path
from .views import UserRecommendationsView

urlpatterns = [
    path('user/', UserRecommendationsView.as_view(), name='user_recommendations'),
]