# api/models.py
from django.db import models
from django import forms

class ChatRoom(models.Model): # 채팅방 나타내는 모델 
    room_id = models.CharField(max_length=225)

    def __str__(self):
        return self.room_id

class Message(models.Model): # 채팅방을 참조하는 것 
    chat_room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE) # 채팅방 나타내는 모델과 연관 / 메시지는 하나의 채팅방에만 속할 수 있기에 만든 것 
    content = models.TextField() # 채팅방 내용 
    created_at = models.DateTimeField(auto_now_add=True) # 채팅 생성된 시간 
    sender = models.TextField() # assistant / user

    def __str__(self):
        return self.content
    
import uuid

class Post(models.Model):
    id = models.UUIDField(primary_key=True, default= uuid.uuid4, editable=False)  # UUID 필드 추가
    title = models.CharField(max_length=100)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    likes = models.IntegerField(default=0)
    job = models.CharField(max_length=100, null=True, blank=True)  # 예시 필드
    titleimage = models.ImageField(upload_to='images/', null=True, blank=True)  # 예시 필드
    place = models.CharField(max_length=100, null=True, blank=True)  # 예시 필드
    available = models.BooleanField(default=True)  # 예시 필드
    review = models.TextField(null=True, blank=True)  # 예시 필드

    def __str__(self):
        return self.title
    
class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'content']  # 필요한 필드들


class CounselingSession(models.Model):
    student_name = models.CharField(max_length=100)  # 학생 이름 필드
    pdf_file = models.FileField(upload_to='pdfs/')    # PDF 파일 필드
    # 추가 필드가 필요하면 여기에 정의

    def __str__(self):
        return self.student_name
    

class FieldTrip(models.Model):
    id = models.UUIDField(primary_key=True, default= uuid.uuid4, editable=False)  # UUID 필드 추가
    title = models.CharField(max_length=200)
    description = models.TextField()
    date = models.DateField()  # 견학 날짜
    place = models.CharField(max_length=100)  # 장소
    image = models.ImageField(upload_to='field_trip_images/')  # 견학 사진
    is_active = models.BooleanField(default=True)  # 모집 여부
    is_completed = models.BooleanField(default=False)  # 마감 여부
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
    

class ChatMessage(models.Model):
    SENDER_CHOICES = (
        ('user', 'User'),
        ('assistant', 'Assistant'),
    )

    chat_room = models.ForeignKey(ChatRoom, related_name='messages', on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)