import re

def run_validator(state: dict):
    sql = state.get("generated_sql", "").lower()
    
    # Check for destructive operations
    forbidden_keywords = ["drop", "delete", "update", "insert", "alter", "truncate", "grant", "revoke"]
    
    for kw in forbidden_keywords:
        if re.search(rf"\b{kw}\b", sql):
            state["is_valid_sql"] = False
            state["errors"] = f"Unsafe SQL detected: contains '{kw}'. Only SELECT statements are allowed."
            return state
            
    if not sql.startswith("select"):
        state["is_valid_sql"] = False
        state["errors"] = "SQL must start with SELECT."
        return state
        
    state["is_valid_sql"] = True
    state["errors"] = ""
    return state