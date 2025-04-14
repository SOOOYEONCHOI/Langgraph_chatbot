import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from langchain_community.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import HumanMessage
from langchain.document_loaders import PyPDFLoader
from langchain.vectorstores import FAISS
from langchain.embeddings.openai import OpenAIEmbeddings
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# OpenAI API 키를 환경 변수에서 가져오기
chat_model = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.7,
    openai_api_key=os.getenv("OPENAI_API_KEY")
)

# 1. FastAPI 앱 초기화
app = FastAPI()

# 2. LangGraph 기반 설정
# OpenAI의 gpt-4o-mini 모델을 사용하여 챗봇 생성

# 3. PDF 문서 로드 및 RAG 설정
# data 폴더의 PDF 파일을 읽어 벡터 데이터베이스 생성
data_folder = "./data"
pdf_files = [os.path.join(data_folder, f) for f in os.listdir(data_folder) if f.endswith(".pdf")]
documents = []
for pdf_file in pdf_files:
    loader = PyPDFLoader(pdf_file)
    documents.extend(loader.load())

# 문서 임베딩 및 벡터스토어 생성
embeddings = OpenAIEmbeddings()
vector_store = FAISS.from_documents(documents, embeddings)

# 4. 요청 데이터 모델 정의
# 사용자가 보낸 질문 데이터를 처리하기 위한 데이터 모델
class ChatRequest(BaseModel):
    question: str

# 5. 응답 데이터 모델 정의
# 챗봇이 생성한 응답 데이터를 반환하기 위한 데이터 모델
class ChatResponse(BaseModel):
    answer: str
    department: str
    similar_questions: list[str]

# 6. 질문/답변 엔드포인트 정의
@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        # Step 1: 민원 유형에 따른 관련 부서 도출
        department_prompt = ChatPromptTemplate.from_template(
            """
            다음 민원의 담당 부서를 도출하세요:
            민원 내용: {question}
            """
        )
        department_message = department_prompt.format_messages(question=request.question)
        department_response = chat_model([HumanMessage(content=department_message[0].content)])
        department = department_response.content.strip()

        # Step 2: 질문에 대한 관련 문서 검색 (RAG) - 유사도 필터링 추가
        search_results_with_scores = vector_store.similarity_search_with_score(request.question, k=10)
        similarity_threshold = 0.8  # 유사도 임계값 (0.0 ~ 1.0)
        filtered_results = [
            doc for doc, score in search_results_with_scores if score >= similarity_threshold
        ]
        related_docs = "\n".join([doc.page_content for doc in filtered_results])

        # Step 3: 유사한 질문 5개 도출
        similar_questions_prompt = ChatPromptTemplate.from_template(
            """
            다음 질문과 유사한 질문 5개를 생성하세요:
            질문: {question}
            """
        )
        similar_questions_message = similar_questions_prompt.format_messages(question=request.question)
        similar_questions_response = chat_model([HumanMessage(content=similar_questions_message[0].content)])
        similar_questions = similar_questions_response.content.strip().split("\n")

        # Step 4: 응답 생성
        response_prompt = ChatPromptTemplate.from_template(
            """
            사용자의 질문: {question}
            관련 문서 내용: {related_docs}
            위 정보를 바탕으로 사용자 질문에 대한 답변을 생성하세요.
            """
        )
        response_message = response_prompt.format_messages(
            question=request.question,
            related_docs=related_docs
        )
        final_response = chat_model([HumanMessage(content=response_message[0].content)])

        # Step 5: 결과 반환
        return ChatResponse(
            answer=final_response.content,
            department=department,
            similar_questions=similar_questions
        )
    except Exception as e:
        # 오류 처리
        raise HTTPException(status_code=500, detail=f"오류 발생: {str(e)}")

# 7. 기본 라우트 정의
@app.get("/")
async def root():
    return {"message": "LangGraph 기반 챗봇 서비스입니다. /chat 엔드포인트를 사용하세요."}