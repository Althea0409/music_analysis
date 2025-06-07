from django.contrib import admin
from .models import Song, Comment

admin.site.register(Song)
admin.site.register(Comment)