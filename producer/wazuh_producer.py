import requests
from kafka import KafkaProducer
import json
import time
import os
from datetime import datetime, timezone

KAFKA_BROKER = "localhost:9092"
TOPIC = "wazuh-alerts"

WAZUH_URL = "https://127.0.0.1:9200/wazuh-alerts-*/_search"
WAZUH_USER = os.getenv("WAZUH_USER")
WAZUH_PASS = os.getenv("WAZUH_PASS")
WAZUH_CA_CERT = "/etc/wazuh-indexer/certs/root-ca.pem"

OFFSET_FILE = "/home/dahfa/wazuh_producer.offset"
POLL_INTERVAL = 5

if not WAZUH_USER or not WAZUH_PASS:
    raise Exception("WAZUH_USER or WAZUH_PASS environment variable not set")

producer = KafkaProducer(
    bootstrap_servers=KAFKA_BROKER,
    value_serializer=lambda v: json.dumps(v).encode("utf-8"),
    acks="all",
    retries=5
)

def load_offset():
    if os.path.exists(OFFSET_FILE):
        with open(OFFSET_FILE, "r") as f:
            return f.read().strip()
    # Kalau belum ada offset → mulai dari sekarang
    return datetime.now(timezone.utc).isoformat()

def save_offset(ts):
    with open(OFFSET_FILE, "w") as f:
        f.write(ts)

last_timestamp = load_offset()

print("🚀 Wazuh Producer started")
print(f"➡ Starting from timestamp: {last_timestamp}")

while True:
    try:
        query = {
            "size": 100,
            "sort": [{"@timestamp": {"order": "asc"}}],
            "query": {
                "range": {"@timestamp": {"gt": last_timestamp}}
            }
        }

        response = requests.get(
            WAZUH_URL,
            auth=(WAZUH_USER, WAZUH_PASS),
            headers={"Content-Type": "application/json"},
            data=json.dumps(query),
            verify=WAZUH_CA_CERT,
            timeout=10
        )

        response.raise_for_status()
        data = response.json()
        hits = data.get("hits", {}).get("hits", [])

        if hits:
            print(f"📦 New alerts: {len(hits)}")

        for hit in hits:
            alert = hit["_source"]

            producer.send(TOPIC, alert)
            last_timestamp = alert.get("@timestamp")

            save_offset(last_timestamp)

            print("✔ Sent:", alert.get("rule", {}).get("description"))

        producer.flush()

    except Exception as e:
        print("❌ Error:", str(e))

    time.sleep(POLL_INTERVAL)
