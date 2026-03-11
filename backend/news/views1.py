from .models import PageLayout
import os
import zipfile
import xml.etree.ElementTree as ET
from django.http import FileResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from .models import (
    Article,
    ArticleImage,
    ArticleVersion,
    Category,
    ArticleActivity
)

from .forms import ArticleForm


@login_required
def reporter_dashboard(request):

    articles = Article.objects.filter(reporter=request.user)

    return render(request, 'news/reporter_dashboard.html', {
        'articles': articles
    })


@login_required
def create_article(request):

    categories = Category.objects.all()

    if request.method == 'POST':

        title = request.POST.get('title')
        content = request.POST.get('content')
        category_id = request.POST.get('category')

        category = Category.objects.get(id=category_id)

        role = request.user.userprofile.role

        # Set initial status depending on role
        if role == 'reporter':
            status = 'submitted'
        elif role == 'subeditor':
            status = 'subeditor_review'
        elif role == 'editor':
            status = 'editor_approved'
        else:
            status = 'submitted'

        article = Article.objects.create(
            title=title,
            content=content,
            category=category,
            reporter=request.user,
            status=status
        )

        # Activity log
        ArticleActivity.objects.create(
            article=article,
            user=request.user,
            action=f"{role.capitalize()} created the article"
        )

        images = request.FILES.getlist('images')
        captions = request.POST.getlist('captions')

        for i, image in enumerate(images):

            caption = ""

            if i < len(captions):
                caption = captions[i]

            ArticleImage.objects.create(
                article=article,
                image=image,
                caption=caption
            )

        # Redirect based on role
        if role == 'reporter':
            return redirect('/reporter-dashboard/')
        elif role == 'subeditor':
            return redirect('/subeditor-dashboard/')
        elif role == 'editor':
            return redirect('/editor-dashboard/')

    return render(request, 'news/create_article.html', {
        'categories': categories
    })

from django.db.models import Q


@login_required
def subeditor_dashboard(request):

    articles = Article.objects.filter(
        status__in=['submitted', 'subeditor_review', 'editor_sent_back']
    )

    search_query = request.GET.get('search')
    category_filter = request.GET.get('category')
    status_filter = request.GET.get('status')

    if search_query:
        articles = articles.filter(
            Q(title__icontains=search_query) |
            Q(content__icontains=search_query)
        )

    if category_filter:
        articles = articles.filter(category__id=category_filter)

    if status_filter:
        articles = articles.filter(status=status_filter)

    categories = Category.objects.all()

    new_articles = Article.objects.filter(status='submitted').count()

    sent_back_articles = Article.objects.filter(
        status='editor_sent_back'
    ).count()

    return render(request, 'news/subeditor_dashboard.html', {
        'articles': articles,
        'categories': categories,
        'new_articles': new_articles,
        'sent_back_articles': sent_back_articles
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

            ArticleActivity.objects.create(
                article=article,
                user=request.user,
                action="Editor approved the article"
            )

            return redirect('/editor-dashboard/')

        elif role == 'subeditor':

            article.status = 'subeditor_review'

            article.save()

            ArticleActivity.objects.create(
                article=article,
                user=request.user,
                action="SubEditor edited the article"
            )

            return redirect('/subeditor-dashboard/')

    versions = article.versions.all().order_by('-edited_at')
    activities = article.activities.all().order_by('-created_at')

    return render(request, 'news/edit_article.html', {
        'article': article,
        'versions': versions,
        'activities': activities
    })


@login_required
def editor_dashboard(request):

    articles = Article.objects.filter(status='subeditor_review')

    pending_articles = articles.count()

    return render(request, 'news/editor_dashboard.html', {
        'articles': articles,
        'pending_articles': pending_articles
    })


@login_required
def approve_article(request, article_id):

    article = Article.objects.get(id=article_id)

    if request.method == 'POST':

        page_number = request.POST.get('page_number')

        if page_number:
            article.page_number = int(page_number)
        else:
            article.page_number = None

        article.status = 'editor_approved'

        article.save()

        ArticleActivity.objects.create(
            article=article,
            user=request.user,
            action="Editor approved the article"
        )

        return redirect('/editor-dashboard/')

    return render(request, 'news/approve_article.html', {
        'article': article
    })


@login_required
def pagination_dashboard(request):

    articles = Article.objects.filter(status='editor_approved')

    ready_for_pagination = articles.count()

    return render(request, 'news/pagination_dashboard.html', {
        'articles': articles,
        'ready_for_pagination': ready_for_pagination
    })


@login_required
def publish_article(request, article_id):

    article = Article.objects.get(id=article_id)

    article.status = 'published'
    article.save()

    ArticleActivity.objects.create(
        article=article,
        user=request.user,
        action="Paginator published the article"
    )

    return redirect('/pagination-dashboard/')


@login_required
def send_back_to_subeditor(request, article_id):

    article = Article.objects.get(id=article_id)

    if request.method == 'POST':

        comment = request.POST.get('editor_comment')

        article.editor_comment = comment
        article.status = 'editor_sent_back'

        article.save()

        ArticleActivity.objects.create(
            article=article,
            user=request.user,
            action="Editor sent article back",
            comment=comment
        )

        return redirect('/editor-dashboard/')

    return render(request, 'news/send_back.html', {
        'article': article
    })


@login_required
def restore_version(request, version_id):

    version = ArticleVersion.objects.get(id=version_id)

    article = version.article

    # Save current version
    ArticleVersion.objects.create(
        article=article,
        title=article.title,
        content=article.content,
        edited_by=request.user
    )

    article.title = version.title
    article.content = version.content
    article.save()

    ArticleActivity.objects.create(
        article=article,
        user=request.user,
        action="Editor restored an old version"
    )

    return redirect(f'/edit-article/{article.id}/')

@login_required
def export_article_xml(request, article_id):

    article = Article.objects.get(id=article_id)

    export_dir = f"/home/ubuntu/newsroom/exports/article_{article.id}"

    if not os.path.exists(export_dir):
        os.makedirs(export_dir)

    xml_file = os.path.join(export_dir, "article.xml")

    root = ET.Element("article")

    title = ET.SubElement(root, "title")
    title.text = article.title

    category = ET.SubElement(root, "category")
    category.text = article.category.name

    page = ET.SubElement(root, "page")
    page.text = str(article.page_number)

    reporter = ET.SubElement(root, "reporter")
    reporter.text = article.reporter.username

    content = ET.SubElement(root, "content")
    content.text = article.content

    images_node = ET.SubElement(root, "images")

    images = ArticleImage.objects.filter(article=article)

    for img in images:

        image_node = ET.SubElement(images_node, "image")

        file_node = ET.SubElement(image_node, "file")
        filename = os.path.basename(img.image.path)
        file_node.text = filename

        caption_node = ET.SubElement(image_node, "caption")
        caption_node.text = img.caption

        # copy image into export folder
        os.system(f"cp {img.image.path} {export_dir}/{filename}")

    tree = ET.ElementTree(root)
    tree.write(xml_file)

    zip_path = f"/home/ubuntu/newsroom/exports/article_{article.id}.zip"

    with zipfile.ZipFile(zip_path, 'w') as zipf:

        zipf.write(xml_file, "article.xml")

        for img in images:
            filename = os.path.basename(img.image.path)
            zipf.write(f"{export_dir}/{filename}", filename)

    return FileResponse(open(zip_path, 'rb'), as_attachment=True)

@login_required
def page_layout_planner(request):

    page_number = request.GET.get("page", 1)

    # Layouts already assigned to this page
    layouts = PageLayout.objects.filter(page_number=page_number)

    used_articles = layouts.values_list("article_id", flat=True)

    # Only show articles assigned to this page
    articles = Article.objects.filter(
        status="editor_approved",
        page_number=page_number
    ).exclude(id__in=used_articles)

    return render(request, "news/page_layout_planner.html", {
        "articles": articles,
        "layouts": layouts,
        "page_number": page_number
    })


from django.http import JsonResponse


from django.http import JsonResponse

@login_required
def save_page_layout(request):

    if request.method == "POST":

        article_id = request.POST.get("article_id")
        slot_number = request.POST.get("slot_number")
        page_number = request.POST.get("page_number")

        article = Article.objects.get(id=article_id)

        PageLayout.objects.filter(
            page_number=page_number,
            slot_number=slot_number
        ).delete()

        PageLayout.objects.create(
            page_number=page_number,
            slot_number=slot_number,
            article=article
        )

        return JsonResponse({"status": "saved"})

import os
import zipfile
import xml.etree.ElementTree as ET
from django.http import FileResponse


@login_required
def export_page_package(request, page_number):

    layouts = PageLayout.objects.filter(page_number=page_number)

    export_dir = f"/home/ubuntu/newsroom/exports/page_{page_number}"

    if not os.path.exists(export_dir):
        os.makedirs(export_dir)

    zip_path = f"/home/ubuntu/newsroom/exports/page_{page_number}.zip"

    for layout in layouts:

        article = layout.article

        xml_file = f"{export_dir}/article_{article.id}.xml"

        root = ET.Element("article")

        title = ET.SubElement(root, "title")
        title.text = article.title

        category = ET.SubElement(root, "category")
        category.text = article.category.name

        page = ET.SubElement(root, "page")
        page.text = str(article.page_number)

        reporter = ET.SubElement(root, "reporter")
        reporter.text = article.reporter.username

        content = ET.SubElement(root, "content")
        content.text = article.content

        images_node = ET.SubElement(root, "images")

        images = ArticleImage.objects.filter(article=article)

        for img in images:

            image_node = ET.SubElement(images_node, "image")

            file_node = ET.SubElement(image_node, "file")

            filename = os.path.basename(img.image.path)

            file_node.text = filename

            caption_node = ET.SubElement(image_node, "caption")

            caption_node.text = img.caption

            os.system(f"cp {img.image.path} {export_dir}/{filename}")

        tree = ET.ElementTree(root)

        tree.write(xml_file)

    with zipfile.ZipFile(zip_path, 'w') as zipf:

        for file in os.listdir(export_dir):

            zipf.write(
                os.path.join(export_dir, file),
                file
            )

    return FileResponse(open(zip_path, 'rb'), as_attachment=True)
