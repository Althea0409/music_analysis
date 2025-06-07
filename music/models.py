from django.db import models

class Song(models.Model):
    """
    歌曲信息表
    """
    song_id = models.CharField(max_length=32, unique=True, verbose_name="歌曲ID")
    name = models.CharField(max_length=128, verbose_name="歌名")
    artist = models.CharField(max_length=128, verbose_name="歌手")
    album = models.CharField(max_length=128, blank=True, verbose_name="专辑")
    hot = models.IntegerField(default=0, verbose_name="热度")

    def __str__(self):
        return self.name

class Comment(models.Model):
    """
    歌曲评论表
    """
    song = models.ForeignKey(Song, on_delete=models.CASCADE, verbose_name="所属歌曲")
    content = models.TextField(verbose_name="评论内容")
    like_count = models.IntegerField(default=0, verbose_name="点赞数")
    sentiment = models.FloatField(default=0.0, verbose_name="情感得分")  # 0-1，越大越正面

    def __str__(self):
        return self.content[:20]