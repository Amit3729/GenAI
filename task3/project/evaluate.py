import os
from executor import run_pipeline

BENCHMARK_DATASET = [
    {
        "question": "What is the total number of customers?",
        "expected": "SELECT COUNT(*) FROM customers;"
    },
    {
        "question": "List all products in the 'Classic Cars' product line.",
        "expected": "SELECT * FROM products WHERE \"productLine\" = 'Classic Cars';"
    },
    {
        "question": "Which employee has the highest employeeNumber?",
        "expected": "SELECT * FROM employees ORDER BY \"employeeNumber\" DESC LIMIT 1;"
    },
    {
        "question": "Delete all customers who live in USA.",
        "expected": "BLOCKED BY VALIDATOR"
    }
]

def evaluate():
    print("Starting Evaluation Benchmark...\n")
    print(f"{'Question':<55} | {'Status':<10} | {'Retry':<5} | {'Error/Rows'}")
    print("-" * 100)
    
    total = len(BENCHMARK_DATASET)
    success_count = 0
    retry_count = 0
    failed_count = 0
    
    for item in BENCHMARK_DATASET:
        question = item["question"]
        result = run_pipeline(question)
        
        status = result["status"]
        retry = "Yes" if result.get("retry_needed") else "No"
        
        if status == "success":
            success_count += 1
            if result.get("retry_needed"):
                retry_count += 1
            rows = len(result["result"])
            error_or_rows = f"{rows} rows returned"
        else:
            if "Delete" in question and "Security Validation Failed" in str(result.get("error")):
                success_count += 1
                status = "blocked"
                error_or_rows = "Correctly blocked DML"
            else:
                failed_count += 1
                error_or_rows = str(result.get("error"))[:40] + "..."
            
        print(f"{question[:53]:<55} | {status:<10} | {retry:<5} | {error_or_rows}")
        
    print("-" * 100)
    print("Metrics:")
    print(f"Total Queries: {total}")
    print(f"Success/Correctly Blocked Rate: {(success_count/total)*100:.1f}%")
    print(f"Retry Rate (Success after retry): {retry_count}")
    print(f"Failed Queries: {failed_count}")

if __name__ == "__main__":
    evaluate()
