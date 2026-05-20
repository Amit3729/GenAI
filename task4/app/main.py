from fastapi import FastAPI
from pydantic import BaseModel
from graph.workflow import build_workflow

app = FastAPI(title="Text to SQL API")

class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    answer: str
    sql: str
    errors: str

def process_query(query: str):
    workflow_app = build_workflow()
    initial_state = {
        "user_query": query,
        "plan": "",
        "generated_sql": "",
        "is_valid_sql": True,
        "execution_results": None,
        "final_answer": "",
        "errors": "",
        "retry_count": 0
    }
    
    final_state = workflow_app.invoke(initial_state)
    return final_state

@app.post("/query", response_model=QueryResponse)
def execute_query(request: QueryRequest):
    result = process_query(request.query)
    return QueryResponse(
        answer=result.get("final_answer", ""),
        sql=result.get("generated_sql", ""),
        errors=result.get("errors", "")
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)