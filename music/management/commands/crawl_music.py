import requests
from django.core.management.base import BaseCommand
from music.models import Song, Comment
from snownlp import SnowNLP
from bs4 import BeautifulSoup

class Command(BaseCommand):
    help = '爬取网易云音乐多个榜单及评论'

    def handle(self, *args, **kwargs):
        # 定义要爬取的榜单及其ID
        toplists = {
            '热歌榜': '3778678',
            '新歌榜': '3779629',
            '飙升榜': '19723756',
        }
        headers = {'User-Agent': 'Mozilla/5.0'}
        for toplist_name, toplist_id in toplists.items():
            # 访问榜单页面
            url = f'https://music.163.com/discover/toplist?id={toplist_id}'
            res = requests.get(url, headers=headers)
            soup = BeautifulSoup(res.text, 'lxml')
            # 获取榜单歌曲（只取前10首）
            songs = soup.select('ul.f-hide li a')
            for s in songs[:10]:
                song_id = s['href'].split('=')[1]
                name = s.text
                # 获取歌曲详情
                song_url = f'https://music.163.com/api/song/detail/?id={song_id}&ids=[{song_id}]'
                song_json = requests.get(song_url, headers=headers).json()
                if 'songs' in song_json and song_json['songs']:
                    song_info = song_json['songs'][0]
                    # 获取歌手名和专辑名
                    artist = song_info.get('artists', [{}])[0].get('name', '未知')
                    album = song_info.get('album', {}).get('name', '未知')
                    # 保存歌曲信息，带榜单字段
                    song_obj, _ = Song.objects.get_or_create(song_id=song_id, defaults={
                        'name': name, 'artist': artist, 'album': album, 'toplist': toplist_name
                    })
                    # 获取热门评论
                    comment_url = f'https://music.163.com/api/v1/resource/comments/R_SO_4_{song_id}?limit=20'
                    comment_json = requests.get(comment_url, headers=headers).json()
                    for c in comment_json.get('hotComments', []):
                        content = c['content']
                        like_count = c['likedCount']
                        # 情感分析
                        sentiment = SnowNLP(content).sentiments
                        # 保存评论
                        Comment.objects.get_or_create(song=song_obj, content=content, defaults={
                            'like_count': like_count, 'sentiment': sentiment
                        })
                else:
                    print(f"未获取到歌曲信息，song_id={song_id}")
                    continue
        self.stdout.write(self.style.SUCCESS('爬取完成！'))