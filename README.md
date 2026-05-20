# GenAI

## Text-to-SQL Agentic Workflow

This project implements an intelligent, agent-driven workflow (powered by LangGraph and LLMs) to convert natural language questions into safe, executable PostgreSQL queries, and then summarize the database results into plain English. 

The core flow involves multiple specialized agents working together as a state machine:

1. **Planner Agent**: Analyzes the user's natural language query against the database schema. It formulates a strategic plan, determining which tables to join and what columns to query or aggregate.
2. **SQL Generator Agent**: Takes the user query and the planner's strategy to write a robust PostgreSQL `SELECT` statement. This agent is specifically prompted to manage PostgreSQL-specific nuances (like wrapping camelCase column names in double quotes).
3. **Validator Agent**: Safety first! This agent ensures that the generated SQL is restricted to read-only `SELECT` statements. It actively blocks destructive operations like `DROP`, `DELETE`, `UPDATE`, `INSERT`, `ALTER`, or `TRUNCATE`. If a query is deemed unsafe or invalid, the workflow instantly bounces back.
4. **Executor Agent**: The system securely executes the validated SQL query against the deployed PostgreSQL database using SQLAlchemy. If an execution error occurs (e.g., syntax issues or missing tables), the error is caught and routed *back* to the SQL Generator via an auto-feedback loop (up to a defined retry limit).
5. **Summarizer Agent**: Takes the raw JSON/dictionary results returned from the database and constructs a friendly, conversational answer to the original user query.

### Architecture Highlights
* **LangGraph**: Orchestrates the agents as individual nodes in a state graph, with conditional edges managing error-correction loops.
* **FastAPI**: Serves external HTTP requests dynamically.
* **Streamlit**: Provides users with an interactive, chat-based UI and transparency tools (to peek inside the AI's logic, see the generated SQL, and inspect raw DB results).
* **Docker Compose**: Containerizes both the Python application environments and the PostgreSQL database seamlessly.