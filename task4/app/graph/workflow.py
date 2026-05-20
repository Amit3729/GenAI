from typing import TypedDict, Any, Dict
from langgraph.graph import StateGraph, END
from agents import run_planner, run_sql_generator, run_validator, run_executor, run_summarizer

class WorkflowState(TypedDict):
    user_query: str
    plan: str
    generated_sql: str
    is_valid_sql: bool
    execution_results: Any
    final_answer: str
    errors: str
    retry_count: int

def validate_and_route(state: WorkflowState):
    if state.get("is_valid_sql", False):
        return "executor"
    else:
        if state.get("retry_count", 0) > 3:
            return END
        return "sql_generator"

def route_execution(state: WorkflowState):
    if state.get("execution_results") is not None and state.get("is_valid_sql", True):
        return "summarizer"
    else:
        if state.get("retry_count", 0) > 3:
            return END
        return "sql_generator"

def increment_retry(state: WorkflowState):
    if not state.get("is_valid_sql", True) or state.get("execution_results") is None:
        state["retry_count"] = state.get("retry_count", 0) + 1
    return state
    
def build_workflow():
    workflow = StateGraph(WorkflowState)
    
    workflow.add_node("planner", run_planner)
    
    # Needs a small wrapper to increment retry on failures
    def generator_node(s):
        s = increment_retry(s)
        return run_sql_generator(s)
        
    workflow.add_node("sql_generator", generator_node)
    workflow.add_node("validator", run_validator)
    workflow.add_node("executor", run_executor)
    workflow.add_node("summarizer", run_summarizer)
    
    workflow.set_entry_point("planner")
    workflow.add_edge("planner", "sql_generator")
    workflow.add_edge("sql_generator", "validator")
    
    workflow.add_conditional_edges("validator", validate_and_route, {
        "executor": "executor",
        "sql_generator": "sql_generator",
        END: END
    })
    
    workflow.add_conditional_edges("executor", route_execution, {
        "summarizer": "summarizer",
        "sql_generator": "sql_generator",
        END: END
    })
    
    workflow.add_edge("summarizer", END)
    
    return workflow.compile()