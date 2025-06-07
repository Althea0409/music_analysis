from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),  # 首页
    path('song/<str:song_id>/', views.song_detail, name='song_detail'),  # 歌曲详情
]