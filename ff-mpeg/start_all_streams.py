from tasks import process_stream

channels = [
    ("geo", "udp://239.1.1.8:1111"),
    ("ary", "udp://239.1.1.9:1111"),
    ("hum", "udp://239.1.1.18:1111"),
    ("neo", "udp://239.1.1.13:1111"),
    ("samaa", "udp://239.1.1.6:1111"),
    ("dawn", "udp://239.1.1.27:1111"),
    ("gtv", "udp://239.1.1.45:1111"),
    ("abn", "udp://239.1.1.57:1111"),
    ("such", "udp://239.1.1.15:1111"),
    ("pnn", "udp://239.1.1.38:1111"),
]

for name, url in channels:
    process_stream.delay(name, url)

print("✅ All channel tasks have been dispatched to Celery workers.")
