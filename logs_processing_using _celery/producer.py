import re
import json
from confluent_kafka import Producer

log_file_path = "../logs/Hadoop_2k.log"
producer = Producer({'bootstrap.servers': 'localhost:9092'})

LOG_PATTERN = re.compile(
    r'(?P<timestamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d+)\s+'
    r'(?P<level>[A-Z]+)\s+'
    r'\[(?P<thread>[^\]]+)\]\s+'
    r'(?P<logger>[^\:]+):\s+'
    r'(?P<message>.*)'
)

def read_log_file(file_path):
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            if line.strip():
                yield line.strip()

def parse_log_line(line):
    match = LOG_PATTERN.match(line)
    if match:
        return match.groupdict()
    return {"raw": line}

def send_to_kafka(file_path, topic):
    for line in read_log_file(file_path):
        parsed = parse_log_line(line)
        producer.produce(topic=topic, value=json.dumps(parsed))
        producer.poll(0)
    producer.flush()
    print("✅ All logs sent to Kafka topic:", topic)

if __name__ == "__main__":
    send_to_kafka(log_file_path, "system-logs")
