from celery import Celery
import json
from datetime import datetime

# Celery app configuration
app = Celery('tasks', broker='redis://localhost:6379/0')

LOG_FILE = "parsed_logs.jsonl"

@app.task
def process_log(log_record):
    """
    Celery task that writes a single log entry to a JSONL file asynchronously.
    """
    try:
        # Convert string to dict if needed
        if isinstance(log_record, str):
            try:
                log_record = json.loads(log_record)
            except json.JSONDecodeError:
                log_record = {"raw": log_record}

        # Write log to JSONL file
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_record, ensure_ascii=False) + "\n")

        print(f"✅ [{datetime.now()}] Log saved by Celery worker.")
    except Exception as e:
        print(f"❌ Error in process_log: {e}")
