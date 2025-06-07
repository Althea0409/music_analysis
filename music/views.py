from django.shortcuts import render, get_object_or_404
from .models import Song, Comment
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import io, base64

def index(request):
    """
    首页：展示热歌榜
    """
    songs = Song.objects.all().order_by('-hot')[:10]
    return render(request, 'music/index.html', {'songs': songs})

def song_detail(request, song_id):
    """
    歌曲详情页：展示评论、情感分析、词云
    """
    song = get_object_or_404(Song, song_id=song_id)
    comments = Comment.objects.filter(song=song)
    # 情感统计
    pos = sum(1 for c in comments if c.sentiment > 0.6)
    neg = sum(1 for c in comments if c.sentiment < 0.4)
    neu = len(comments) - pos - neg
    # 生成词云图片
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
        'song': song, 'comments': comments,
        'pos': pos, 'neg': neg, 'neu': neu,
        'wordcloud': image_base64
    })