from django.urls import path
from . import views

urlpatterns = [

    path('reporter-dashboard/', views.reporter_dashboard, name='reporter_dashboard'),

    path('create-article/', views.create_article, name='create_article'),

    path('subeditor-dashboard/', views.subeditor_dashboard, name='subeditor_dashboard'),

    path('edit-article/<int:article_id>/', views.edit_article, name='edit_article'),

    path('editor-dashboard/', views.editor_dashboard, name='editor_dashboard'),

    path('approve-article/<int:article_id>/', views.approve_article, name='approve_article'),

    path('pagination-dashboard/', views.pagination_dashboard, name='pagination_dashboard'),

    path('publish-article/<int:article_id>/', views.publish_article, name='publish_article'),

]
