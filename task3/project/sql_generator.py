import os
import json
from openai import OpenAI
from dotenv import load_dotenv
from prompts.templates import SCHEMA_CONTEXT, DECOMPOSE_PROMPT, GENERATE_SQL_PROMPT, FIX_SQL_PROMPT

load_dotenv()

# Using Groq's OpenAI-compatible endpoint
client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)
# Using the requested model
MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

def decompose_query(question: str) -> dict:
    """LLM Call 1: Decompose the natural language query into JSON."""
    prompt = DECOMPOSE_PROMPT.format(question=question)
    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1
    )
    content = response.choices[0].message.content.strip()
    if content.startswith("```json"):
        content = content[7:-3].strip()
    elif content.startswith("```"):
        content = content[3:-3].strip()
        
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        return {"error": "Failed to parse decomposition as JSON", "raw_content": content}

def generate_sql(question: str, decomposition: dict) -> str:
    """LLM Call 2: Generate the raw SQL query based on decomposition and schema."""
    prompt = GENERATE_SQL_PROMPT.format(
        schema=SCHEMA_CONTEXT,
        decomposition=json.dumps(decomposition, indent=2),
        question=question
    )
    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1
    )
    content = response.choices[0].message.content.strip()
    if content.startswith("```sql"):
        content = content[6:-3].strip()
    elif content.startswith("```"):
        content = content[3:-3].strip()
    return content

def fix_sql(original_query: str, error_message: str) -> str:
    """LLM Call 3: Fix a failed SQL query based on the DB error."""
    prompt = FIX_SQL_PROMPT.format(
        schema=SCHEMA_CONTEXT,
        original_query=original_query,
        error_message=error_message
    )
    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1
    )
    content = response.choices[0].message.content.strip()
    if content.startswith("```sql"):
        content = content[6:-3].strip()
    elif content.startswith("```"):
        content = content[3:-3].strip()
    return content
