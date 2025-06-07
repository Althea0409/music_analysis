import requests
from django.core.management.base import BaseCommand
from music.models import Song, Comment
from snownlp import SnowNLP
from bs4 import BeautifulSoup

class Command(BaseCommand):
    help = '爬取网易云音乐热歌榜及评论'

    def handle(self, *args, **kwargs):
        # 网易云热歌榜URL
        url = 'https://music.163.com/discover/toplist?id=3778678'
        headers = {'User-Agent': 'Mozilla/5.0'}
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
            print(song_json)  # 调试用，正式使用可注释掉

            # 检查返回内容是否包含'songs'且不为空
            if 'songs' in song_json and song_json['songs']:
                song_info = song_json['songs'][0]
                # 获取歌手名（注意是 artists，不是 ar）
                artist = song_info.get('artists', [{}])[0].get('name', '未知')
                # 获取专辑名（注意是 album，不是 al）
                album = song_info.get('album', {}).get('name', '未知')
                # 保存歌曲信息
                song_obj, _ = Song.objects.get_or_create(song_id=song_id, defaults={
                    'name': name, 'artist': artist, 'album': album
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