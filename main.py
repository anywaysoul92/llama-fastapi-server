from llama_cpp import Llama
from fastapi import FastAPI, Body


# Llama 모델 로드 
llm = Llama(
    model_path="./models/Llama-3.2-1B-Instruct-Q4_K_M.gguf",
    n_ctx=4096,
    n_threads=2,
    verbose=False,
    chat_format="llama-3",
)

# 언어 모델에게 규칙을 지정하는 최상위 지시문 

SYSTEM_PROMPT = (
    "You are a concise assistant. "
    "Always reply in the same language as the user's input. "
    "Do not change the language. "
    "Do not mix languages."
)

app = FastAPI()

@app.post("/chat")
def generate_chat_handler(
    # {"user_input:": "Python이 뭐야?"}
    user_input: str = Body(..., embed=True), #mbed=True json object로 읽어옴
):
    result = llm.create_chat_completion(
    messages=[
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_input},
    ],
    max_tokens=256,
    temperature= 0.7, # 1에 가까울 수록 창의적인 대답이 나온다
)
    return {"result": result["choices"][0]["message"]["content"].strip()}

