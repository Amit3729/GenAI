from langchain_groq import ChatGroq
from config import settings

def get_llm():
    # Groq currently offers models like llama-3.1-70b-versatile, mixtral-8x7b-32768, etc.
    # While they do not host a direct "gpt oss 120b" model, Llama 3 70B is currently their 
    # largest/most capable open-source model available on the platform for general use.
    return ChatGroq(
        temperature=0, 
        api_key=settings.GROQ_API_KEY, 
        model_name="llama-3.3-70b-versatile"
    )