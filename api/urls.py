# api/urls.py
from django.urls import path
from .views import PDFQuestionView, create_chat_room
from api.views import TestOpenAIView
from .views import home, send_message
from .views import post_list, post_create, post_detail, post_like, apply
from .views import field_trip_list, current_field_trips, completed_field_trips, field_trip_reviews


urlpatterns = [
    path('send-message/', send_message, name='send_message'),  # 메시지 전송 API
    path('upload-pdf/', PDFQuestionView.as_view(), name='upload_pdf'),  # PDF 업로드 API
    path('create-chat-room/', create_chat_room, name='create_chat_room'),
    path('test-openai/', TestOpenAIView.as_view(), name='test_openai'),
    #path('', home, name='home'),

    # 게시판 관련 URL
    path('posts/', post_list, name='post-list'),  # 게시판 목록
    path('posts/create/', post_create, name='post-create'),  # 게시글 작성
    path('posts/<uuid:post_id>/', post_detail, name='post_detail'),  # 게시글 상세
    path('posts/<uuid:post_id>/like/', post_like, name='post_like'),  # 게시글 좋아요

    # 견학 활동 관련 URL
    path('field-trips/', field_trip_list, name='field-trip-list'),  # 견학 활동 목록
    path('field-trips/current/', current_field_trips, name='current-field-trips'),  # 현재 모집 중인 견학 활동
    path('field-trips/completed/', completed_field_trips, name='completed-field-trips'),  # 마감된 견학 활동
    path('field-trips/<int:trip_id>/reviews/', field_trip_reviews, name='field-trip-reviews'),  # 견학 활동 후기

    # 신청하기
    path('apply/', apply, name='apply'),  # 신청하기
]