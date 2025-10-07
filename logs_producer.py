import re
import time
from confluent_kafka import Producer
import json
log_file_path= "./logs/Hadoop_2k.log"

producer = Producer({'bootstrap.servers': 'localhost:9092'})


LOG_PATTERN = re.compile(
    r'(?P<timestamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d+)\s+'
    r'(?P<level>[A-Z]+)\s+'
    r'\[(?P<thread>[^\]]+)\]\s+'
    r'(?P<logger>[^\:]+):\s+'
    r'(?P<message>.*)'
)

# LOG_PATTERN = re.compile(
#     r'(?P<timestamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}) - '
#     r'(?P<level>[A-Z]+)\s+\[(?P<thread>[^\]]+)\] - (?P<message>.*)'
# )

def read_log_file(file_path):
    with open(file_path, 'r',encoding='utf-8', errors='ignore') as file:
        for line in file:  
            if not line:
                continue
            yield line.strip()
            # time.sleep(0.05)

def parse_log_line(line):
    match = LOG_PATTERN.match(line)
    if match:
        return match.groupdict()
    return {"raw": line}  # fallback if pattern doesn’t match

def send_to_kafka(log_file_path,topic):
    for line in read_log_file(log_file_path):
        parsed_line = parse_log_line(line)
        producer.produce(topic=topic, value=json.dumps(parsed_line))
        producer.poll(0)
    producer.flush()
    print("✅ Logs sent to Kafka topic:", topic)


send_to_kafka(log_file_path,"system-logs")