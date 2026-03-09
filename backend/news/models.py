from django.db import models
from django.contrib.auth.models import User


# News Categories
class Category(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


# News Article
class Article(models.Model):

    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('subeditor_review', 'SubEditor Review'),
        ('editor_approved', 'Editor Approved'),
        ('pagination', 'Pagination'),
        ('published', 'Published'),
    ]

    title = models.CharField(max_length=500)

    content = models.TextField()

    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE
    )

    reporter = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default='draft'
    )

    # Page number assigned by editor
    page_number = models.IntegerField(
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return self.title


# Article Images (multiple images per article)
class ArticleImage(models.Model):

    article = models.ForeignKey(
        Article,
        on_delete=models.CASCADE,
        related_name='images'
    )

    image = models.ImageField(
        upload_to='article_images/'
    )

    caption = models.CharField(
        max_length=255,
        blank=True
    )

    uploaded_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"Image for {self.article.title}"
