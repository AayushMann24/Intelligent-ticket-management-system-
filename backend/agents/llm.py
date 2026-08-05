from langchain_ollama import ChatOllama


LLM_MODEL = "llama3.2"

llm = ChatOllama(
    model=LLM_MODEL,
    temperature=0,
    num_predict=512,
)