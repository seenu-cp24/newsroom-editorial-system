from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Article
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

        if form.is_valid():

            article = form.save(commit=False)
            article.reporter = request.user
            article.status = 'submitted'
            article.save()

            return redirect('reporter_dashboard')

    else:
        form = ArticleForm()

    return render(request, 'news/create_article.html', {
        'form': form
    })

@login_required
def subeditor_dashboard(request):

    articles = Article.objects.filter(status='submitted')

    return render(request, 'news/subeditor_dashboard.html', {
        'articles': articles
    })


@login_required
def edit_article(request, article_id):

    article = Article.objects.get(id=article_id)

    if request.method == 'POST':

        article.title = request.POST['title']
        article.content = request.POST['content']

        article.status = 'subeditor_review'

        article.save()

        return redirect('/subeditor-dashboard/')

    return render(request, 'news/edit_article.html', {
        'article': article
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

        page_number = request.POST['page_number']

        article.page_number = page_number

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
