from agents.llm import get_llm
from langchain_core.messages import SystemMessage, HumanMessage
from prompts import SUMMARIZER_PROMPT
import json

def run_summarizer(state: dict):
    query = state["user_query"]
    results = state.get("execution_results", [])
    
    llm = get_llm()
    content_str = f"User Query: {query}\n\nDatabase Results:\n{json.dumps(results, default=str)}"
    
    messages = [
        SystemMessage(content=SUMMARIZER_PROMPT),
        HumanMessage(content=content_str)
    ]
    response = llm.invoke(messages)
    state["final_answer"] = response.content
    return state