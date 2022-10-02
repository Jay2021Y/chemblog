from django.urls import path
from . import views

app_name = 'chemblog'

urlpatterns = [
    path('', views.index, name='index'),
    path('post/<int:post_id>/', views.post_detail, name='post_detail'),
    path('post/create/', views.post_create, name='post_create'),
    path('post/modify/<int:post_id>', views.post_modify, name='post_modify'),
    path('post/delete/<int:post_id>', views.post_delete, name='post_delete'),
    path('post/vote/<int:post_id>', views.post_vote, name='post_vote'),
    path('comment/vote/<int:comment_id>', views.comment_vote, name='comment_vote'),
    path('comment/delete<int:comment_id>', views.comment_delete, name='comment_delete'),
]
