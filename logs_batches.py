import json
import time
from confluent_kafka import Consumer

consumer = Consumer({
    'bootstrap.servers': 'localhost:9092',
    'group.id': 'log-group',
    'auto.offset.reset': 'earliest'
})

consumer.subscribe(["system-logs"])


BUFFER = []
BUFFER_SIZE = 500        
FLUSH_INTERVAL = 2       
last_flush_time = time.time()
COUNT=0
def flush_buffer():
    """Write buffer to file in one go"""
    global BUFFER, last_flush_time, COUNT
    if not BUFFER:
        return
    COUNT=0
    with open("logs.jsonl", "a") as f:
        f.write("\n".join(json.dumps(rec) for rec in BUFFER))
        f.write("\n")  # ensure newline at the end


    print(f"✅ Flushed {len(BUFFER)} logs to file.")
    BUFFER.clear()
    last_flush_time = time.time()

def consume_logs():
    global last_flush_time, COUNT

    print("Starting buffered Kafka consumer...")
    try:
        while True:
            msg = consumer.poll(1.0)
            if msg is None:
                # Periodic flush
                if time.time() - last_flush_time >= FLUSH_INTERVAL:
                    flush_buffer()
                continue

            if msg.error():
                print("Error:", msg.error())
                continue

            raw_value = msg.value().decode('utf-8', errors='replace')
            try:
                log_entry = json.loads(raw_value)
            except json.JSONDecodeError:
                log_entry = {"raw": raw_value}

            BUFFER.append(log_entry)
            COUNT+=1
            print(f"Buffered log #{COUNT}")
            # Flush if buffer full
            if len(BUFFER) >= BUFFER_SIZE:
                flush_buffer()

    except KeyboardInterrupt:
        print("Stopping consumer...")
    finally:
        flush_buffer()  # Final flush before exit
        consumer.close()

if __name__ == "__main__":
    consume_logs()