from tools.db_tools import execute_query

def run_executor(state: dict):
    sql = state.get("generated_sql", "")
    if state.get("is_valid_sql", False):
        try:
            results = execute_query(sql)
            if isinstance(results, str) and results.startswith("Execution Error"):
                state["execution_results"] = None
                state["errors"] = results
                state["is_valid_sql"] = False # Send back to generator
            else:
                state["execution_results"] = results
        except Exception as e:
            state["execution_results"] = None
            state["errors"] = str(e)
            state["is_valid_sql"] = False
    return state