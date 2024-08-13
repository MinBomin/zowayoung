# api/views.py
from django.http import JsonResponse
from django.views import View
from .models import ChatRoom, Message
import json
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
import os
import uuid
from .forms import PostForm
from .open_ai import consultant, client
from pydantic import BaseModel

class consult_template(BaseModel):
    content: str
    jobs_list : list[str]

def zigi_chat(prompt):
    completion = client.beta.chat.completions.parse(
        model='gpt-4o-mini',
        messages=[
            {"role": "system", "content": """너는 한국인 중고등학생을 대상으로 상담을 진행하는 진로 상담가야. Question을 바탕으로 도움을 줘! 답변은 종결어미로 '용'을 쓰는 '용용체'를 써줘!
            최종적인 목표는 어떤 진로를 가지면 좋을 지 3가지를 추천해줘. 관련 레퍼런스도 제공해주면 좋을 것 같아. 레퍼런스는 진로에 관한 설명이 들어가있는 글 등이 좋을 것 같아. 아래는 답변의 형태의 예시야. 답변의 예시보다는 더 구체적인 설명이 많이 들어가면 좋을 것 같아.

            Question : 진로 선택에 대해 고민하고 있습니다. 도움을 줄 수 있을까요? 평소 좋아하는 취미생활은 그림 그리기입니다. 평소 좋아하는 과목은 미술입니다. 제 전시를 사람들이 좋아해줄 때 행복해요.
            Answer : 좋아하는 과목과 취미 생활을 보니 미술 쪽으로 진로를 잡아보면 어떨까요? 현재 미술 분야의 전망은 다음과 같습니다. 최종적으로 추천 드리는 직업은 1. 미술가, 2. 그래픽 디자이너, 3. 일러스트레이터입니다.
             response_format of json foramt like:
             {
                'content' : Answer,
                'jobs_list' : ['미술가', '그래픽 디자이너', '일러스트레이터']
             }
             """
            }, 
            {"role": "user", "content": prompt},
        ],
        response_format=consult_template,
    )
    results = completion.choices[0].message.content
    return results

@method_decorator(csrf_exempt, name='dispatch')
class TestOpenAIView(View):
    def post(self, request, *args, **kwargs):
        user_message = "안녕하세요, 오늘 날씨는 어때요?"
        ai_response = zigi_chat(user_message)  # OpenAI API 호출
        return JsonResponse({'ai_response': ai_response}, status=200)

def get_chat_history(chat_room_id):
    # 데이터베이스에서 채팅 기록을 가져오는 로직 구현
    # 예시: ChatMessage.objects.filter(chat_room_id=chat_room_id)
    messages = Message.objects.filter(chat_room_id=chat_room_id).values_list('content', flat=True)
    return list(messages)

def create_prompt(chat_history, message):
    # 채팅 기록과 새 메시지를 결합하여 프롬프트 생성
    prompt = "\n".join(chat_history) + f"\nUser: {message}\nAI:"
    return prompt

async def get_ai_response(prompt):
    # OpenAI API 호출
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    return response['choices'][0]['message']['content']

@csrf_exempt
def create_chat_room(request):
    if request.method == 'POST':
        # UUID를 사용하여 고유한 chat_room_id 생성
        chat_room_id = str(uuid.uuid4())
        
        # ChatRoom 객체 생성
        chat_room = ChatRoom.objects.create(room_id=chat_room_id)
        
        return JsonResponse({'room_id': chat_room.room_id}, status=201)

    return JsonResponse({'error': 'POST 요청이 필요합니다.'}, status=400)

questions = [
    '평소 좋아하는 취미 생활이 뭐예요?',
    '평소 좋아하는 과목이 뭐예요?',
    '어떤 것을 할 때 가장 즐거우신가요?'
]
questions.reverse()
answers = [
]

@csrf_exempt
def send_message(request):
    if request.method == 'POST':
        room_id = request.POST.get('room_id')
        user_message = request.POST.get('message')

        if not room_id or not user_message:
            return JsonResponse({'error': '채팅방 ID와 메시지가 필요합니다.'}, status=400)

        if (len(questions) > 0):
            if (len(answers) > 0):
                answers.append(user_message)
            return JsonResponse({'response': questions.pop() }, status=200)

        # AI에 요청하고 응답 받기
        ai_response = zigi_chat(','.join(answers))

        # 메시지 저장
        #chat_room = get_object_or_404(ChatRoom, room_id=room_id)
        
        # 사용자 메시지 저장
        #chat_room.messages.create(content=user_message, sender='user')

        # AI 응답 생성 (예시)
        #ai_response = "AI의 대답입니다."  # 여기서 실제 AI 응답 로직을 추가해야 합니다.
        
        # AI 응답 저장
        #chat_room.messages.create(content=ai_response, sender='ai')

        return JsonResponse({'response': ai_response}, status=200)

from django.core.files.storage import FileSystemStorage
import asyncio

from django.shortcuts import render

def home(request):
    return render(request, 'index.html')


from .open_ai import PDFAssistant  # OpenAI 파일에서 클래스 임포트
from django.core.files.storage import FileSystemStorage
from openai import OpenAI
from typing import Optional
from django.views import View
from django.http import JsonResponse

class PDFQuestionView(View):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.assistant = PDFAssistant()  # 환경 변수에서 API 키 가져오기
        
    def post(self, request):
        # 요청에서 파일과 질문을 가져옵니다.
        #if 'file' not in request.FILES or 'question' not in request.POST:
            #return JsonResponse({'error': 'File and question are required'}, status=400)

        uploaded_file = request.FILES['file']
        question = "이거어덤" #request.POST['question']

        # 파일 저장
        fs = FileSystemStorage()
        filename = fs.save(uploaded_file.name, uploaded_file)
        file_path = fs.path(filename)  # 파일의 실제 경로 가져오기

        # 질문에 대한 답변 요청
        try:
            answers = self.assistant.get_answers(file_path, question)  # 인스턴스의 메서드 호출
            return JsonResponse({'answers': answers}, status=200)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)


#게시판


from .models import Post
from .forms import PostForm
import json

# 게시글 목록 조회
def post_list(request):
    if request.method == 'GET':
        posts = Post.objects.all()  # 모든 게시글 가져오기
        data = [{"id": post.id, "title": post.title, "content": post.content} for post in posts]
        return JsonResponse(data, safe=False)  # JSON 응답 반환
    return JsonResponse({'error': '잘못된 요청 방법입니다.'}, status=405)

# 게시글 작성
@csrf_exempt  # CSRF 보호 비활성화 (개발 환경에서만 사용)
def post_create(request):
    if request.method == 'POST':
        if request.content_type == 'application/json':
            try:
                data = json.loads(request.body.decode('utf-8'))
                title = data['title']
                content = data['content']
                review_text = data.get('review')  # 후기를 선택적으로 가져옴

                post = Post.objects.create(title=title, content=content)  # 게시글 생성

                # 후기가 있을 경우 게시글에 추가
                if review_text:
                    # 후기를 게시글에 저장하는 방법 (리스트나 다른 모델 사용 가능)
                    post.reviews.create(text=review_text)  # 별도의 리뷰 모델을 가정
                    post.save()

                return JsonResponse({'message': '게시글이 생성되었습니다.', 'id': str(post.id)}, status=201)
            except json.JSONDecodeError:
                return JsonResponse({'error': '잘못된 JSON 형식입니다.'}, status=400)
            except KeyError:
                return JsonResponse({'error': '필수 필드가 누락되었습니다.'}, status=400)
        else:
            return JsonResponse({'error': 'Content-Type은 application/json이어야 합니다.'}, status=400)
    return JsonResponse({'error': '잘못된 요청 방법입니다.'}, status=405)

# 게시글 상세 보기
def post_detail(request):
    post = get_object_or_404(Post, id=request.GET['post_id'])
    return JsonResponse({
        'id': post.id,
        'title': post.title,
        'content': post.content,
        'likes': post.likes,
        'created_at': post.created_at,
        'job': post.job,
        'titleimage': post.titleimage.url if post.titleimage else None,  # 이미지 URL 처리
        'place': post.place,
        'available': post.available,
        'review': post.review,
    })

# 좋아요 누르기
@csrf_exempt
def post_like(request):
    post_id = request.GET['post_id']
    post = get_object_or_404(Post, id=post_id)
    post.likes += 1
    post.save()
    return JsonResponse({'likes': post.likes})



#신청하기 버튼 

def apply(request):
    if request.method == 'POST':
        # 실제로 데이터 저장은 하지 않음
        return JsonResponse({'message': '신청되었습니다.'}, status=200)
    return JsonResponse({'error': '잘못된 요청 방법입니다.'}, status=405)


from .models import FieldTrip # 진로와 관련된 견학 활동 
from django.http import JsonResponse

def field_trip_list(request):
    field_trips = FieldTrip.objects.filter(is_active=True)  # 활성화된 견학 활동 조회
    data = [{
        "id": trip .id,
        "title": trip.title,
        "location": trip.place,  # 위치
        "date": trip.date.strftime("%Y-%m-%d"),  # 날짜 (형식 조정)
        "image": trip.image.url if trip.image else None  # 사진 (이미지가 없을 경우 None)
    } for trip in field_trips]
    return JsonResponse(data, safe=False)

def current_field_trips(request):  # 현재 모집 중인 견학 활동
    current_trips = FieldTrip.objects.filter(is_active=True, is_completed=False)  # 현재 모집 중인 견학 활동
    data = [{
        "id": trip.id,
        "title": trip.title,
        "location": trip.place,  # 위치
        "date": trip.date.strftime("%Y-%m-%d"),  # 날짜 (형식 조정)
        "image": trip.image.url if trip.image else None  # 사진 (이미지가 없을 경우 None)
    } for trip in current_trips]
    return JsonResponse(data, safe=False)

def completed_field_trips(request):  # 마감된 견학 활동
    completed_trips = FieldTrip.objects.filter(is_completed=True)  # 마감된 견학 활동
    data = [{
        "id": trip.id,
        "title": trip.title,
        "location": trip.place,  # 위치
        "date": trip.date.strftime("%Y-%m-%d"),  # 날짜 (형식 조정)
        "image": trip.image.url if trip.image else None  # 사진 (이미지가 없을 경우 None)
    } for trip in completed_trips]
    return JsonResponse(data, safe=False)


def field_trip_reviews(request):  # 견학활동 후기 
    field_trip = get_object_or_404(FieldTrip, id=request.GET['trip_id'])
    if request.method == 'POST':
        # 후기를 작성하는 로직
        review_text = request.POST.get('review')
        # 간단한 예시, 실제로는 리뷰 리스트로 관리하는 것이 좋습니다.
        field_trip.reviews.create(text=review_text)  # 별도의 리뷰 모델을 가정
        field_trip.save()
        return JsonResponse({'message': '후기가 등록되었습니다.'})
    
    # 리뷰 조회
    reviews = field_trip.reviews.all()  # 리뷰 리스트 가져오기
    review_list = [{'id': review.id, 'text': review.text} for review in reviews]
    return JsonResponse({'reviews': review_list})