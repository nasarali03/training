from confluent_kafka import Consumer
from tasks import process_log  # Import Celery task
import json
import ast

consumer = Consumer({
    "bootstrap.servers": "localhost:9092",
    "group.id": "logs-group",
    "auto.offset.reset": "earliest"
})

consumer.subscribe(["system-logs"])

def safe_decode(b):
    if b is None:
        return None
    if isinstance(b, bytes):
        try:
            return b.decode("utf-8")
        except UnicodeDecodeError:
            return b.decode("utf-8", errors="replace")
    return str(b)

def consume_logs():
    print("🚀 Kafka Consumer started (using Celery for writing)...")
    try:
        while True:
            msg = consumer.poll(1.0)
            if msg is None:
                print("⏳ Waiting for messages...")
                continue
            if msg.error():
                print("❌ Error:", msg.error())
                continue

            raw_value = safe_decode(msg.value())
            if not raw_value:
                continue

            # Try to parse JSON, fallback to raw string
            try:
                data = json.loads(raw_value)
            except json.JSONDecodeError:
                try:
                    data = ast.literal_eval(raw_value)
                except Exception:
                    data = {"raw": raw_value}

            # 🔥 Send to Celery asynchronously
            process_log.delay(data)
            consumer.commit(asynchronous=True)
            print(f"📤 Sent log to Celery: {data}")

    except KeyboardInterrupt:
        print("🛑 Stopping consumer...")
    finally:
        consumer.close()

if __name__ == "__main__":
    consume_logs()
