from sqlalchemy import text
from db import engine

def execute_query(sql_query: str) -> list[dict] | str:
    """Execute SQL query safely and return results."""
    try:
        with engine.connect() as conn:
            result = conn.execute(text(sql_query))
            if result.returns_rows:
                return [dict(row._mapping) for row in result]
            else:
                conn.commit()
                return "Query executed successfully, no rows returned."
    except Exception as e:
        return f"Execution Error: {str(e)}"