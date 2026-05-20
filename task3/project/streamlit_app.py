import streamlit as st
from executor import run_pipeline

st.set_page_config(page_title="Text-to-SQL Pipeline", layout="wide")

st.title("Text-to-SQL with Prompt Chaining")
st.markdown("Ask natural language questions to query the `classicmodels` database.")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if message["role"] == "user":
            st.markdown(message["content"])
        else:
            st.markdown(message["content"])
            if "data" in message:
                st.dataframe(message["data"])
            if "sql" in message:
                with st.expander("View SQL & Debug Info"):
                    st.code(message["sql"], language="sql")
                    if message.get("retry_needed"):
                        st.warning("⚠️ Query required 1 retry to fix a database error.")
                    if message.get("decomposition"):
                        st.json(message["decomposition"])

user_input = st.chat_input("Ask a question about your database (e.g., 'Show me all customers in France')")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Processing prompt chain (Decompose -> Generate -> Validate -> Execute)..."):
            result = run_pipeline(user_input)
            
            if result["status"] == "success":
                response_text = f"Successfully executed query. Found {len(result['result'])} rows."
                st.markdown(response_text)
                st.dataframe(result["result"])
                with st.expander("View SQL & Debug Info"):
                    st.code(result["sql"], language="sql")
                    if result.get("retry_needed"):
                        st.warning("⚠️ Query required 1 retry to fix a database error.")
                    st.json(result["decomposition"])
                    
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": response_text,
                    "data": result["result"],
                    "sql": result["sql"],
                    "retry_needed": result.get("retry_needed"),
                    "decomposition": result.get("decomposition")
                })
            else:
                response_text = f"**Error:** {result['error']}"
                st.error(response_text)
                with st.expander("View Generated SQL (Failed)"):
                    if result.get("sql"):
                        st.code(result["sql"], language="sql")
                    if result.get("decomposition"):
                        st.json(result.get("decomposition"))
                        
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response_text,
                    "sql": result.get("sql"),
                    "decomposition": result.get("decomposition")
                })
