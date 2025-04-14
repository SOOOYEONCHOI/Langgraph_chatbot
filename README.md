# LangGraph 기반 민원 챗봇

LangGraph와 FastAPI를 활용하여 민원 질문에 대한 답변을 제공하는 챗봇 서비스입니다.  
이 챗봇은 다음과 같은 주요 기능을 제공합니다:
- 민원 유형에 따른 관련 부서 도출
- 질문과 관련된 문서를 검색(RAG)
- 유사한 질문 5개 생성
- GPT 모델을 활용한 최종 답변 생성

---

## 📋 주요 기능
1. **민원 유형 분류 및 관련 부서 도출**  
   사용자의 질문을 분석하여 민원의 유형을 분류하고 담당 부서를 도출합니다.

2. **RAG (Retrieval-Augmented Generation)**  
   질문과 관련된 문서를 벡터 DB(FAISS)를 사용하여 검색하고, 유사도가 높은 문서만 필터링하여 답변 생성에 활용합니다.

3. **유사 질문 생성**  
   사용자의 질문과 유사한 질문 5개를 생성하여 추가적인 정보를 제공합니다.

4. **GPT 기반 응답 생성**  
   질문, 관련 문서, 민원 유형 정보를 바탕으로 GPT 모델을 활용하여 최종 답변을 생성합니다.

---

## 설치 및 실행

### 1. 필요한 패키지 설치
Python 3.8 이상이 필요합니다. 아래 명령어를 실행하여 필요한 패키지를 설치하세요:
```bash
pip install fastapi uvicorn langchain-community langchain-openai python-dotenv faiss-cpu
```

### 2. `.env` 파일 설정
프로젝트 루트 디렉토리에 `.env` 파일을 생성하고 아래 내용을 추가하세요:
```env
OPENAI_API_KEY=your_openai_api_key
```
- `OPENAI_API_KEY`: OpenAI API 키를 입력하세요.

### 3. 관련 문서 PDF 파일 추가**
`data` 폴더를 생성하고, 검색에 사용할 PDF 파일을 해당 폴더에 추가하세요:
```bash
mkdir data
# PDF 파일 추가
```

### 5. **FastAPI 서버 실행**
아래 명령어를 실행하여 FastAPI 서버를 시작하세요:
```bash
uvicorn main:app --reload
```

---

## 사용법

### 1. **Swagger UI를 통한 테스트**
브라우저에서 아래 URL로 이동하여 Swagger UI를 사용해 API를 테스트할 수 있습니다:
```
http://127.0.0.1:8000/docs
```

### 2. **POST 요청으로 질문 보내기**
`/chat` 엔드포인트에 POST 요청을 보내 질문을 처리합니다. 예:
```json
POST http://127.0.0.1:8000/chat
Content-Type: application/json

{
    "question": "도로 파손 신고는 어디에 해야 하나요?"
}
```

### 3. **응답 예시**
```json
{
    "answer": "도로 파손 신고는 도로 관리 부서에 문의하세요.",
    "department": "도로 관리 부서",
    "similar_questions": [
        "도로 파손 신고 절차는?",
        "도로 보수 요청은 어디로 해야 하나요?",
        "도로 관련 민원은 어디에 접수하나요?",
        "도로 파손 신고를 위한 연락처는?",
        "도로 문제를 해결하려면 어떻게 해야 하나요?"
    ]
}
```

---

## 📂 프로젝트 구조
```
langgraph-chatbot/
├── main.py               # FastAPI 서버 및 챗봇 로직
├── .env                  # 환경 변수 파일
├── data/                 # PDF 문서 저장 폴더
├── requirements.txt      # 필요한 Python 패키지 목록
└── README.md             # 프로젝트 설명 파일
```

---

## 참고 사항
- **유사도 임계값**: RAG 검색에서 유사도 임계값(`similarity_threshold`)은 기본적으로 0.8로 설정되어 있습니다. 필요에 따라 값을 조정하세요.
- **PDF 문서 업데이트**: 새로운 PDF 문서를 추가한 경우, 서버를 재시작하여 벡터 DB를 갱신하세요.

---