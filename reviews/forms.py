from django import forms
from .models import Review

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.RadioSelect,
            'comment': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Ваш отзыв...'}),
        }