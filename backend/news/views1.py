from .models import Article, ArticleImage, ArticleVersion
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
'''from .models import Article'''
from .forms import ArticleForm


@login_required
def reporter_dashboard(request):

    articles = Article.objects.filter(reporter=request.user)

    return render(request, 'news/reporter_dashboard.html', {
        'articles': articles
    })

@login_required
def create_article(request):

    if request.method == 'POST':

        form = ArticleForm(request.POST)

        images = request.FILES.getlist('images')
        captions = request.POST.getlist('captions')

        if form.is_valid():

            article = form.save(commit=False)
            article.reporter = request.user
            article.status = 'submitted'
            article.save()

            for i, image in enumerate(images):

                caption = ""

                if i < len(captions):
                    caption = captions[i]

                ArticleImage.objects.create(
                    article=article,
                    image=image,
                    caption=caption
                )

            return redirect('/reporter-dashboard/')

    else:
        form = ArticleForm()

    return render(request, 'news/create_article.html', {
        'form': form
    })


@login_required
def subeditor_dashboard(request):

    articles = Article.objects.filter(
        status__in=['submitted', 'subeditor_review']
    )

    return render(request, 'news/subeditor_dashboard.html', {
        'articles': articles
    })

@login_required
def edit_article(request, article_id):

    article = Article.objects.get(id=article_id)

    if request.method == 'POST':

        # Save previous version
        ArticleVersion.objects.create(
            article=article,
            title=article.title,
            content=article.content,
            edited_by=request.user
        )

        article.title = request.POST['title']
        article.content = request.POST['content']

        role = request.user.userprofile.role

        if role == 'editor':

            page_number = request.POST.get('page_number')

            if not page_number:
                return render(request, 'news/edit_article.html', {
                    'article': article,
                    'versions': article.versions.all().order_by('-edited_at'),
                    'error': 'Page number is required before approval'
                })

            article.page_number = int(page_number)
            article.status = 'editor_approved'

            article.save()

            return redirect('/editor-dashboard/')

        elif role == 'subeditor':

            article.status = 'subeditor_review'

            article.save()

            return redirect('/subeditor-dashboard/')

    versions = article.versions.all().order_by('-edited_at')

    return render(request, 'news/edit_article.html', {
        'article': article,
        'versions': versions
    })

@login_required
def editor_dashboard(request):

    articles = Article.objects.filter(status='subeditor_review')

    return render(request, 'news/editor_dashboard.html', {
        'articles': articles
    })


@login_required
def approve_article(request, article_id):

    article = Article.objects.get(id=article_id)

    if request.method == 'POST':

        page_number = request.POST.get('page_number')

        # Convert page number safely
        if page_number:
            article.page_number = int(page_number)
        else:
            article.page_number = None

        article.status = 'editor_approved'

        article.save()

        return redirect('/editor-dashboard/')

    return render(request, 'news/approve_article.html', {
        'article': article
    })


@login_required
def pagination_dashboard(request):

    articles = Article.objects.filter(status='editor_approved')

    return render(request, 'news/pagination_dashboard.html', {
        'articles': articles
    })


@login_required
def publish_article(request, article_id):

    article = Article.objects.get(id=article_id)

    article.status = 'published'

    article.save()

    return redirect('/pagination-dashboard/')

@login_required
def send_back_to_subeditor(request, article_id):

    article = Article.objects.get(id=article_id)

    article.status = 'subeditor_review'

    article.save()

    return redirect('/editor-dashboard/')

@login_required
def restore_version(request, version_id):

    version = ArticleVersion.objects.get(id=version_id)

    article = version.article

    # Save current version before restoring
    ArticleVersion.objects.create(
        article=article,
        title=article.title,
        content=article.content,
        edited_by=request.user
    )

    # Restore old version
    article.title = version.title
    article.content = version.content

    article.save()

    return redirect(f'/edit-article/{article.id}/')
