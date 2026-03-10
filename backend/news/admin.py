from django.contrib import admin
from .models import Category, Article, ArticleImage, ArticleVersion


admin.site.register(Category)
admin.site.register(Article)
admin.site.register(ArticleImage)
admin.site.register(ArticleVersion)
