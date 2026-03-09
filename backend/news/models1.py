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

    def can_edit(self, user):
        """
        Role based editing rules
        """

        if user.userprofile.role == 'reporter':
            return self.reporter == user

        if user.userprofile.role == 'subeditor':
            return self.status == 'submitted'

        if user.userprofile.role == 'editor':
            return self.status == 'subeditor_review'

        if user.userprofile.role == 'paginator':
            return self.status == 'editor_approved'

        return False

    def __str__(self):
        return self.title
