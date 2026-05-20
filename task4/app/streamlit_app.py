import streamlit as st
import json
from main import process_query

st.set_page_config(page_title="Text to SQL Agent", page_icon="🤖")

st.title("🤖 Text to SQL AI Agent")
st.markdown("Ask natural language questions about your PostgreSQL database.")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask a question about the classicmodels data... (e.g., 'What is the sum of payments for customer 112?')"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Processing your query through the agentic workflow..."):
            try:
                result_state = process_query(prompt)
                
                answer = result_state.get("final_answer", "")
                if not answer:
                    answer = f"Error generating answer. Details:\n{result_state.get('errors')}"
                    
                st.markdown(answer)
                st.session_state.messages.append({"role": "assistant", "content": answer})
                
                with st.expander("View Agent Details"):
                    st.write("**Plan:**")
                    st.write(result_state.get("plan", ""))
                    st.write("**Generated SQL:**")
                    st.code(result_state.get("generated_sql", ""), language="sql")
                    st.write("**Raw Results:**")
                    st.json(result_state.get("execution_results", []))
                    if result_state.get("errors"):
                        st.error(result_state.get("errors"))
                        
            except Exception as e:
                st.error(f"Workflow failed: {str(e)}")