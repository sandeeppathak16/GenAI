from fastapi import FastAPI
from langchain_ollama import ChatOllama
from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint

from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

ollama = ChatOllama(model="llama3", temperature=0,)

huggingface = HuggingFaceEndpoint(
    repo_id="Qwen/Qwen3-Coder-Next",
)

chat_model = ChatHuggingFace(llm=huggingface)


@app.post("/chat")
async def root(message: str, model: str):
    if model == 'ollama':
        llm = ollama
    elif model == 'huggingface':
        llm = chat_model

    response = llm.invoke(message)
    return response.content