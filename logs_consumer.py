from confluent_kafka import Consumer
import json
import time
import ast

consumer=Consumer({"bootstrap.servers":"localhost:9092",
                   "group.id":"logs-group",
                   "auto.offset.reset":"earliest"})

consumer.subscribe(["system-logs"])

parsed_logs = []

def safe_decode(b):
    if b is None:
        return None
    
    if isinstance(b, bytes):
        try:
            return b.decode('utf-8')
        except UnicodeDecodeError:
            return b.decode('utf-8', errors='replace')
        
    return str(b)

def consume_logs(output_file):
    try:
        with open(output_file,"a", encoding='utf-8') as f:
            while True:
                    
                msg = consumer.poll(1.0)
                if msg is None:
                    print("waiting....")
                    continue
                if msg.error():
                    print("Error:", msg.error())
                    continue
                print(msg.value())
                raw_value=safe_decode(msg.value())
                if not raw_value:
                    continue
                
                
                
                try:
                    data = json.loads(raw_value)
                except json.JSONDecodeError:
                    
                    try:
                        data = ast.literal_eval(raw_value)
                    except Exception:
                        print("⚠️ Could not parse:", raw_value)
                        continue
                
                f.write(json.dumps(data,ensure_ascii=False)+"\n")
                f.flush()
                parsed_logs.append(data)
                print(data)
                print(f"✅ Received & saved log: {data}")

    except KeyboardInterrupt:
        pass
    finally:
        consumer.close()

consume_logs("Hadoop_parsed.jsonl")
# with open("Hadoop_parsed.json", "w") as f:
#     json.dump(parsed_logs, f, indent=4)

