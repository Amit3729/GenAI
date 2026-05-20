import os
import csv
import json
import psycopg2
from groq import Groq
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")

# Configure Groq
if not GROQ_API_KEY:
    print("Error: GROQ_API_KEY not found in .env")
    exit(1)

client = Groq(api_key=GROQ_API_KEY)

def get_database_schema(db_url):
    """Fetches the database schema (tables and columns) to provide context to the LLM."""
    if not db_url:
        print("Warning: DATABASE_URL not found in .env. Schema context will be empty.")
        return "No database schema provided."
        
    try:
        conn = psycopg2.connect(db_url)
        cur = conn.cursor()
        
        # Query to get tables and columns in the public schema
        cur.execute("""
            SELECT table_name, column_name, data_type
            FROM information_schema.columns
            WHERE table_schema = 'public'
            ORDER BY table_name, ordinal_position;
        """)
        
        schema_info = {}
        for row in cur.fetchall():
            table, column, dtype = row
            if table not in schema_info:
                schema_info[table] = []
            schema_info[table].append(f"{column} ({dtype})")
            
        cur.close()
        conn.close()
        
        schema_text = "Database Schema:\n"
        for table, columns in schema_info.items():
            schema_text += f"Table: {table}\n"
            schema_text += f"Columns: {', '.join(columns)}\n\n"
            
        return schema_text
    except Exception as e:
        print(f"Error fetching schema: {e}")
        return "Schema could not be fetched."

def decompose_query(question, schema_text):
    """Uses Groq to decompose the question into a JSON format."""
    
    prompt = f"""
You are a SQL expert. Given the database schema and a question, decompose the question into a JSON object.

Database Schema Context:
{schema_text}

For the question:
1. Identify the Intent (what is being asked)
2. Identify Tables involved (as a list of strings)
3. Identify Columns needed (as a list of strings)
4. Identify Filters/conditions (as a list of strings)
5. Identify Joins (as a list of strings)

Question:
{question}

You MUST return a valid JSON object matching this schema exactly. DO NOT add any extra text or conversational response.
{{
  "Intent": "Description of intent",
  "Tables": ["table1", "table2"],
  "Columns": ["col1", "col2"],
  "Filters": ["condition1"],
  "Joins": ["join1"]
}}
"""
    
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant that outputs strictly in JSON."
                },
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model="llama-3.3-70b-versatile",
            temperature=0,
            response_format={"type": "json_object"}
        )
        
        text_resp = chat_completion.choices[0].message.content.strip()
        # Clean up in case model adds markdown blocks even with JSON mode
        if text_resp.startswith("```json"):
            text_resp = text_resp[7:]
        elif text_resp.startswith("```"):
            text_resp = text_resp[3:]
        if text_resp.endswith("```"):
            text_resp = text_resp[:-3]
            
        return json.loads(text_resp.strip())
    except Exception as e:
        print(f"Error decomposing query '{question}': {e}")
        return None

def main():
    print("Fetching schema from database...")
    schema_text = get_database_schema(DATABASE_URL)
    
    csv_file_path = "data/sql_questions_only.csv"
    output_csv_path = "data/decomposed_queries.csv"
    
    questions = []
    
    print(f"Reading questions from {csv_file_path}...")
    try:
        with open(csv_file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            # Find the actual question column name (fallback to 'question' if exists, otherwise first column)
            fieldnames = reader.fieldnames
            q_col = 'question' if fieldnames and 'question' in fieldnames else (fieldnames[0] if fieldnames else None)
            
            if not q_col:
                print("Could not find a valid column in the CSV.")
                return
                
            for row in reader:
                questions.append(row[q_col])
    except Exception as e:
        print(f"Error reading CSV: {e}")
        return

    print(f"Loaded {len(questions)} questions.")
    print("Decomposing queries...")
    
    # Prepare the CSV writer
    csv_headers = ["Question", "Intent", "Tables", "Columns", "Filters", "Joins"]
    
    with open(output_csv_path, 'w', encoding='utf-8', newline='') as out_f:
        writer = csv.DictWriter(out_f, fieldnames=csv_headers)
        writer.writeheader()
        
        for i, q in enumerate(questions, 1):
            print(f"Processing question {i}/{len(questions)}: {q}")
            decomposition = decompose_query(q, schema_text)
            
            if decomposition:
                row = {
                    "Question": q,
                    "Intent": decomposition.get("Intent", ""),
                    "Tables": ", ".join(decomposition.get("Tables", [])),
                    "Columns": ", ".join(decomposition.get("Columns", [])),
                    "Filters": ", ".join(decomposition.get("Filters", [])),
                    "Joins": ", ".join(decomposition.get("Joins", []))
                }
                writer.writerow(row)
                out_f.flush()
                print(f"Success! Result: {json.dumps(decomposition)}")
            else:
                writer.writerow({
                    "Question": q,
                    "Intent": "ERROR",
                    "Tables": "",
                    "Columns": "",
                    "Filters": "",
                    "Joins": ""
                })
            
    print(f"Done! Results saved to {output_csv_path}")

if __name__ == "__main__":
    main()
