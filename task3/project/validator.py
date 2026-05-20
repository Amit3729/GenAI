import re

FORBIDDEN_KEYWORDS = [
    "DELETE", "DROP", "UPDATE", "INSERT", "ALTER", "TRUNCATE",
    "REPLACE", "GRANT", "REVOKE", "COMMIT", "ROLLBACK", "EXEC", "EXECUTE"
]

def validate_sql(sql_query: str) -> bool:
    """
    Validates the SQL query to ensure it is a safe SELECT statement.
    Returns True if valid, False if it contains forbidden DML/DDL operations.
    """
    sql_no_comments = re.sub(r'--.*$', '', sql_query, flags=re.MULTILINE)
    sql_no_comments = re.sub(r'/\*.*?\*/', '', sql_no_comments, flags=re.DOTALL)
    
    sql_upper = sql_no_comments.upper()
    
    for keyword in FORBIDDEN_KEYWORDS:
        pattern = rf"\b{keyword}\b"
        if re.search(pattern, sql_upper):
            return False
            
    if not re.search(r"\bSELECT\b", sql_upper):
        return False
        
    return True
