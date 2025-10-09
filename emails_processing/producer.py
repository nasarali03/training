from confluent_kafka import Producer
import json
import os
import time

producer = Producer({'bootstrap.servers': 'localhost:9092'})
topic = "emails"
file_path="email.txt"
def send_to_kafka():
    
    seen_emails=set()
    while True:
        if os.path.exists(file_path):
            with open("email.txt", "r", encoding="utf-8") as file:
                for email in file:
                    email=email.strip()
                    if email and email not in seen_emails:
                        producer.produce(topic=topic, value=json.dumps({"email": email}))
                        seen_emails.add(email)
        time.sleep(2)    
        # producer.flush()
        # producer.close()
    

if __name__ == "__main__":
    send_to_kafka()
