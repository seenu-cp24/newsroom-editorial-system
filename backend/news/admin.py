from django.contrib import admin
from .models import Category, Article, ArticleImage, ArticleVersion, ArticleActivity
from .models import PageLayout


admin.site.register(Category)
admin.site.register(Article)
admin.site.register(ArticleImage)
admin.site.register(ArticleVersion)
admin.site.register(ArticleActivity)
admin.site.register(PageLayout)
