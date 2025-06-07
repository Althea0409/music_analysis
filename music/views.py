from django.shortcuts import render, get_object_or_404, redirect
from .models import Song, Comment
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import io, base64
from django.core.paginator import Paginator

def index(request):
    """
    首页视图：支持榜单切换和搜索
    """
    toplist = request.GET.get('toplist', '热歌榜')  # 当前榜单
    query = request.GET.get('q', '')              # 搜索关键词
    toplists = Song.objects.values_list('toplist', flat=True).distinct()  # 所有榜单
    if query:
        # 搜索模式
        songs = Song.objects.filter(name__icontains=query, toplist=toplist)
    else:
        # 默认显示当前榜单前30首
        songs = Song.objects.filter(toplist=toplist).order_by('-hot')[:30]
    return render(request, 'music/index.html', {
        'songs': songs, 'query': query, 'toplist': toplist, 'toplists': toplists
    })

def song_detail(request, song_id):
    """
    歌曲详情页：评论分页、情感分析、词云
    """
    song = get_object_or_404(Song, song_id=song_id)
    comments = Comment.objects.filter(song=song).order_by('-like_count')
    # 分页，每页10条
    paginator = Paginator(comments, 10)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    # 情感统计
    pos = sum(1 for c in comments if c.sentiment > 0.6)
    neg = sum(1 for c in comments if c.sentiment < 0.4)
    neu = len(comments) - pos - neg
    # 生成词云
    text = ' '.join([c.content for c in comments])
    wc = WordCloud(font_path='msyh.ttc', width=400, height=200, background_color='white').generate(text)
    buf = io.BytesIO()
    plt.figure(figsize=(6,3))
    plt.imshow(wc, interpolation='bilinear')
    plt.axis('off')
    plt.tight_layout()
    plt.savefig(buf, format='png')
    plt.close()
    image_base64 = base64.b64encode(buf.getvalue()).decode()
    return render(request, 'music/song_detail.html', {
        'song': song, 'comments': page_obj,
        'pos': pos, 'neg': neg, 'neu': neu,
        'wordcloud': image_base64
    })