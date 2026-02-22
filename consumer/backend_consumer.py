import json
import redis
import psycopg2
from kafka import KafkaConsumer
from psycopg2.errors import UniqueViolation

# ===== CONFIG =====
KAFKA_BROKER = "localhost:9092"
TOPIC = "wazuh-alerts"
GROUP_ID = "dashboard-group"

POSTGRES_CONFIG = {
    "dbname": "siem",
    "user": "siemuser",
    "password": "Kres@backend123",
    "host": "localhost"
}

REDIS_HOST = "localhost"
REDIS_PORT = 6379
# ==================

# Connect Redis
r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

# Connect Postgre
conn = psycopg2.connect(**POSTGRES_CONFIG)
cursor = conn.cursor()

# Kafka Consumer (manual commit)
consumer = KafkaConsumer(
    TOPIC,
    bootstrap_servers=KAFKA_BROKER,
    group_id=GROUP_ID,
    auto_offset_reset="latest",
    enable_auto_commit=False,
    value_deserializer=lambda m: json.loads(m.decode("utf-8"))
)

print("🟢 Backend consumer started...")

for message in consumer:
    alert = message.value

    event_id = alert.get("id")
    timestamp = alert.get("@timestamp")
    agent = alert.get("agent", {}).get("name")
    level = alert.get("rule", {}).get("level")
    description = alert.get("rule", {}).get("description")
    full_log = alert.get("full_log")

    try:
        cursor.execute(
            """
            INSERT INTO alerts (event_id, timestamp, agent_name, rule_level, rule_description, full_log)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (event_id, timestamp, agent, level, description, full_log)
        )
        conn.commit()

        # Commit offset hanya jika DB insert sukses
        consumer.commit()

    except UniqueViolation:
        conn.rollback()
        print("⚠ Duplicate skipped:", event_id)

    # Update Redis (Realtime layer)
    r.incr("total_alerts")

    if level and level >= 10:
        r.incr("critical_alerts")

    r.lpush("last_50_alerts", json.dumps(alert))
    r.ltrim("last_50_alerts", 0, 49)

    print("✔ Processed:", description)
