from django import forms
from .models import Article, ArticleImage
from django.contrib.auth.models import User
from accounts.models import UserProfile
from news.models import Edition


class ArticleForm(forms.ModelForm):

    class Meta:
        model = Article
        fields = ['title', 'content', 'category']


class ArticleImageForm(forms.ModelForm):

    class Meta:
        model = ArticleImage
        fields = ['image', 'caption']


class CreateUserForm(forms.Form):

    username = forms.CharField(max_length=150)

    email = forms.EmailField()

    password = forms.CharField(widget=forms.PasswordInput)

    role = forms.ChoiceField(
        choices=[
            ("reporter", "Reporter"),
            ("subeditor", "SubEditor"),
            ("editor", "Editor"),
            ("paginator", "Paginator"),
        ]
    )

    edition = forms.ModelChoiceField(
        queryset=Edition.objects.all(),
        required=False
    )
