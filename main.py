import asyncio
from llama_cpp import Llama
from openai import AsyncOpenAI
from fastapi import FastAPI, Body, Request, Depends
from contextlib import asynccontextmanager
# lifespan 불러오는 라이브러리 
from fastapi.responses import StreamingResponse
# fastapi에서 제공하는 class
from config import Settings
from schema import OpenAIResponse



# 언어 모델에게 규칙을 지정하는 최상위 지시문 

SYSTEM_PROMPT = (
    "You are a concise assistant. "
    "Always reply in the same language as the user's input. "
    "Do not change the language. "
    "Do not mix languages."
)

# 모델 준비하는 시간을 확보한다 
@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.llm = Llama( # llm 모델 로드 
        model_path="./models/Llama-3.2-1B-Instruct-Q4_K_M.gguf",
        n_ctx=4096,
        n_threads=2,
        verbose=False,
        chat_format="llama-3",
    )
    app.state.openai_client = AsyncOpenAI(api_key=settings.openai_api_key)
    yield   

app = FastAPI(lifespan=lifespan)

# 요청마다 LLM 객체를 접근할 수 있게 해주는 의존성 함수 
def get_llm(request: Request): # request: Request 의 type hint 를 보고 fastapi 요청임을 알고 처리
    return request.app.state.llm

def get_openai_client(request: Request):
    return request.app.state.openai_client

@app.post("/chat")
async def generate_chat_handler( # streaming response 쓰기위해 async 적용
    # {"user_input:": "Python이 뭐야?"}
    user_input: str = Body(..., embed=True), #mbed=True json object로 읽어옴
    llm = Depends(get_llm),
):
    async def event_generator():
    # CPU-Bound 작업은 대기가 없어서 asyncio 할 수 없다 
    # Thread pool 로 보내서 사용
    # RAG(= Retrieval Augmented Generation)
        result = llm.create_chat_completion(
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_input},
        ],
        max_tokens=256,
        temperature= 0.7, # 1에 가까울 수록 창의적인 대답이 나온다
        stream=True, # 응답을 token 단위로 잘라서 줌 
    )
        for chunk in result:
            token = chunk["choices"] [0] ["delta"].get("content")
            if token:
                yield token
                await asyncio.sleep(0.1)
                # CPU BOUND 작업이라 event loop blocking 방지를 위해 강제 SLEEP 코드

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
    )

    # return {"result": result["choices"][0]["message"]["content"].strip()}


@app.post("/openai")
async def openai_handler(
    user_input: str = Body(..., embed=True),
    openai_client = Depends(get_openai_client),
):
    async def event_generator():
        async with openai_client.responses.stream(
        model="gpt-4.1-mini",
        input=user_input,
        text_format=OpenAIResponse,
        ) as stream:
            async for event in stream:
                # 텍스트 토큰
                if event.type == "response.output_text.delta":
                    yield event.delta
                
                # 연결 종료
                elif event.type == "response.completed":
                    break
        # if response.output_parsed.confidence <= 0.95:
        # return {"msg": "자신이 없습니다."}

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
    )
