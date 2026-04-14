
# 🦙 Llama-FastAPI-Server

> **Llama 3.2 1B Instruct 모델을 FastAPI로 구현한 로컬 LLM 추론 서버입니다.**

## 🛠 Tech Stack
![Python](https://img.shields.io/badge/python-3.13-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688?logo=fastapi)
![Llama.cpp](https://img.shields.io/badge/Llama.cpp-GGUF-black?logo=cpu)

## 🚀 주요 기능
- **Llama-3.2-1B-Instruct-GGUF** 모델 기반 추론
- **FastAPI**를 이용한 가벼운 REST API 서버
- **Swagger UI**를 통한 간편한 API 테스트 지원
- **System Prompt**를 통한 일관된 어시스턴트 페르소나 설정

## ⚙️ 시작하기

### 1. 가상환경 설정 및 필수 패키지 설치
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install "fastapi[standard]" llama-cpp-python --extra-index-url [https://abetlen.github.io/llama-cpp-python/whl/cpu](https://abetlen.github.io/llama-cpp-python/whl/cpu)

2. 모델 다운로드
models/ 폴더 내에 .gguf 파일을 배치합니다.

PowerShell
hf download bartowski/Llama-3.2-1B-Instruct-GGUF Llama-3.2-1B-Instruct-Q4_K_M.gguf --local-dir ./models
3. 서버 실행
PowerShell
fastapi dev main.py

📍 API

서버 실행 후 http://127.0.0.1:8000/docs에서 직접 테스트 가능합니다.

## 📅 2026-04-14 업데이트: 리소스 관리 및 외부 API 연동 최적화
1. 애플리케이션 수명 주기 관리 (Lifespan)
개념: FastAPI의 @asynccontextmanager를 활용해 서버 시작(Startup) 시점에 로컬 LLM과 OpenAI 클라이언트를 한 번만 로드하고, 종료(Shutdown) 시 자원을 해제하도록 아키텍처를 개선했습니다.

리스크 관리: 매 요청마다 모델을 로드하여 발생하는 지연 시간(Latency)과 메모리 고갈 문제를 방지하여 서버 안정성을 확보했습니다.

2. Pydantic Settings를 통한 환경 변수 주입
데이터 검증: Pydantic의 BaseSettings를 통해 .env 파일의 API 키와 설정값을 자동 로드하고 유효성을 검증합니다.

⭐ 자주 틀리는 지점: 클래스 설계도(Settings)만 정의하고 객체 인스턴스화(settings = Settings())를 누락하여 발생하는 AuthenticationError(401) 리스크를 해결했습니다. 변수명 오타로 인한 매핑 실패를 방지하기 위해 오타 점검 확실히 합니다.

3. OpenAI 비동기 스트리밍 (StreamingResponse)
비동기 추론: AsyncOpenAI와 StreamingResponse를 결합하여 사용자에게 토큰 단위로 답변을 실시간 전달하는 스트리밍 환경을 구축했습니다.
