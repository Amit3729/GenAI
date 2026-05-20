import os
import json
from datetime import datetime
from sql_generator import decompose_query, generate_sql, fix_sql
from validator import validate_sql
from database import execute_query

LOG_FILE = os.path.join(os.path.dirname(__file__), "logs", "query_logs.json")

def append_to_log(log_entry: dict):
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, "w") as f:
            json.dump([], f)
            
    with open(LOG_FILE, "r") as f:
        try:
            logs = json.load(f)
        except json.JSONDecodeError:
            logs = []
            
    logs.append(log_entry)
    with open(LOG_FILE, "w") as f:
        json.dump(logs, f, indent=2)

def run_pipeline(question: str) -> dict:
    """Orchestrates the Text-to-SQL Prompt Chaining Workflow."""
    result = {
        "question": question,
        "decomposition": None,
        "sql": None,
        "result": None,
        "status": "failed",
        "error": None,
        "retry_needed": False,
        "timestamp": datetime.now().isoformat()
    }
    
    try:
        decomposition = decompose_query(question)
        result["decomposition"] = decomposition
        if "error" in decomposition:
            result["error"] = decomposition["error"]
            append_to_log(result)
            return result
            
        sql = generate_sql(question, decomposition)
        result["sql"] = sql
        
        if not validate_sql(sql):
            result["error"] = "Security Validation Failed: Query contains forbidden statements or is not a SELECT query."
            append_to_log(result)
            return result
            
        try:
            db_result = execute_query(sql)
            result["result"] = db_result
            result["status"] = "success"
        except Exception as e:
            result["retry_needed"] = True
            error_message = str(e)
            
            fixed_sql = fix_sql(sql, error_message)
            result["sql"] = fixed_sql
            
            if not validate_sql(fixed_sql):
                result["error"] = "Security Validation Failed on Retry."
                append_to_log(result)
                return result
                
            try:
                db_result = execute_query(fixed_sql)
                result["result"] = db_result
                result["status"] = "success"
            except Exception as retry_e:
                result["error"] = f"Retry Failed: {str(retry_e)}"
                
    except Exception as e:
        result["error"] = f"Pipeline Error: {str(e)}"
        
    append_to_log(result)
    return result
