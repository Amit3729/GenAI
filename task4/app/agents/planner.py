from agents.llm import get_llm
from langchain_core.messages import SystemMessage, HumanMessage
from prompts import PLANNER_PROMPT

def run_planner(state: dict):
    query = state["user_query"]
    llm = get_llm()
    messages = [
        SystemMessage(content=PLANNER_PROMPT),
        HumanMessage(content=query)
    ]
    response = llm.invoke(messages)
    state["plan"] = response.content
    return state