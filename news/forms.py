from django import forms
from .models import Post

# news/forms.py

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'subtitle', 'content', 'published_at']

    def clean_title(self):
        title = self.cleaned_data['title']
        # Проверяем, есть ли такой заголовок, но не учитываем текущий объект (при редактировании)
        if Post.objects.filter(title=title).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("Новость с таким заголовком уже существует.")
        return title