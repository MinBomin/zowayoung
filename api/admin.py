# api/admin.py
from django.contrib import admin
from .models import ChatRoom, Post, FieldTrip

admin.site.register(ChatRoom)
admin.site.register(Post)
admin.site.register(FieldTrip)

