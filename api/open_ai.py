from openai import OpenAI
import json, time, os
from pydantic import BaseModel
from typing import List, Optional

MODEL="gpt-4o-mini"

api_key = "key"   # 환경 변수에서 API 키를 가져옴
if not api_key:
    raise ValueError("API 키가 설정되어 있지 않습니다.")
client = OpenAI(api_key=api_key)  # API 키를 설정

class PDFAssistant:
    """
    A class to interact with the OpenAI API to create an assistant for answering questions based on a PDF file.

    Attributes:
        client (OpenAI): Client for interacting with OpenAI API.
        assistant_id (Optional[str]): ID of the created assistant. None until an assistant is created.
    """
    def __init__(self) -> None:
        api_key = "key"   # 환경 변수에서 API 키를 가져옴
        if not api_key:
            raise ValueError("API 키가 설정되어 있지 않습니다.")
        self.client = OpenAI(api_key=api_key)  # API 키를 설정
        self.assistant_id: Optional[str] = None


    def get_answers(self, filepath, question: str) -> List[str]:
        """
        Asks a question to the assistant and retrieves the answers.

        Args:
            question (str): The question to be asked to the assistant.

        Returns:
            List[str]: A list of answers from the assistant.

        Raises:
            ValueError: If the assistant has not been created yet.
        """
        file = self.client.files.create(
            file=open(filepath, 'rb'),
            purpose="assistants"
        )

        assistant = self.client.beta.assistants.create(
            name="PDF Helper",
            instructions="'DONT USE MARKDOWN.' You are my assistant who can answer questions from the given pdf. 너는 한국인 중고등학생을 대상으로 상담을 진행하는 학교생활기록부 작성 도우미야. 첨부파일을 바탕으로 해당 학생이 어느 부분에서 강점과 약점을 가지고 있고 보완해야하는지 설명해줘.",
            tools=[{"type": "file_search"}],
            model=MODEL,
        )
        self.assistant_id = assistant.id
        
        if self.assistant_id is None:
            raise ValueError("Assistant not created. Please upload a file first.")

        thread = self.client.beta.threads.create()

        self.client.beta.threads.messages.create(
            thread_id=thread.id,
            role="assistant",
            content="""
                    """,
            attachments = [{ "file_id": file.id, "tools": [{ "type": "file_search" }] }],
        )

        run = self.client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=self.assistant_id
        )

        while True:
            run_status = self.client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
            time.sleep(10)
            print(run_status)
            if run_status.status == 'completed':
                messages = self.client.beta.threads.messages.list(thread_id=thread.id)
                break
            if run_status.status == 'failed':
                raise "LOL"

        result = [message.content[0].text.value for message in messages.data if message.role == "assistant"]
        
        return result[0]

class consult_template(BaseModel):  
    content: str
    jobs_list : list[str]

def consult_carrer(query:str):
    completion = client.beta.chat.completions.parse(
        model=MODEL,
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
            {"role": "user", "content": query},
        ],
        response_format=consult_template,
    )
    results = completion.choices[0].message.content
    return results



### print(json.loads(consult_carrer("진로 선택에 대해 고민하고 있습니다. 도움을 줄 수 있을까요? 평소 좋아하는 취미생활은 코딩입니다. 평소 좋아하는 과목은 생명과학입니다. 다른 사람과 함께해서 사회에 이바지 하는 활동을 좋아해요.")))

consultant = PDFAssistant()
