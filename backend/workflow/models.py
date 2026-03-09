from django.db import models
from django.contrib.auth.models import User
from news.models import Article


class WorkflowLog(models.Model):

    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('subeditor_review', 'SubEditor Review'),
        ('editor_approved', 'Editor Approved'),
        ('pagination', 'Pagination'),
        ('published', 'Published'),
    ]

    article = models.ForeignKey(
        Article,
        on_delete=models.CASCADE,
        related_name='workflow_logs'
    )

    previous_status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES
    )

    new_status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES
    )

    changed_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    remarks = models.TextField(
        blank=True
    )

    changed_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.article.title} - {self.new_status}"
