from agents.llm import get_llm
from langchain_core.messages import SystemMessage, HumanMessage
from prompts import GENERATOR_PROMPT

def run_sql_generator(state: dict):
    query = state["user_query"]
    plan = state.get("plan", "")
    error = state.get("errors", "")
    
    llm = get_llm()
    instruction = f"User Query: {query}\nPlan: {plan}\n"
    if error:
        instruction += f"\nPrevious Error to fix: {error}\n"
        
    messages = [
        SystemMessage(content=GENERATOR_PROMPT),
        HumanMessage(content=instruction)
    ]
    response = llm.invoke(messages)
    
    sql = response.content.strip().replace("```sql", "").replace("```", "").strip()
    state["generated_sql"] = sql
    return state