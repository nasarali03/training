from confluent_kafka import Consumer
import json
import time

consumer = Consumer({
    'bootstrap.servers': 'localhost:9092',
    'group.id': 'email-group',
    'auto.offset.reset': 'earliest',
})

consumer.subscribe(['emails'])

def consume_messages():
    try:
        while True:
            msg = consumer.poll(1.0)  
            if msg is None:
                print("⏳ Waiting for messages...")
                time.sleep(1)
                continue
            if msg.error():
                print("⚠️ Error:", msg.error())
                continue

            # Decode and parse message
            data = json.loads(msg.value().decode('utf-8'))
            print(f"✅ Received email: {data['email']}")

            # Commit offset (optional)
            consumer.commit(asynchronous=False)

    except KeyboardInterrupt:
        print("\n🛑 Stopping consumer...")
    finally:
        consumer.close()
        print("👋 Consumer closed.")

if __name__ == "__main__":
    consume_messages()
