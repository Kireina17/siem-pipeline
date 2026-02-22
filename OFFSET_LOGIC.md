# 🧠 Offset Logic & Duplicate Protection

## 🎯 Goal

Ensure:

- No duplicate ingestion
- No data loss
- Safe restart
- Safe crash recovery

---

## 🔹 Producer Offset Logic

Producer filters alerts using:

```
@timestamp > last_timestamp
```

This guarantees:
- Old alerts are not reprocessed
- Only new alerts are sent to Kafka

---

## 🔹 Kafka Offset Handling

Consumer uses:

```python
enable_auto_commit=False
consumer.commit()
```

Offset is committed only after:

1. Insert to PostgreSQL successful
2. Redis update successful

If crash occurs before commit:
- Kafka will re-deliver the message
- PostgreSQL ignores duplicate via:

```
UNIQUE(event_id)
ON CONFLICT DO NOTHING
```

---

## 🔐 Duplicate Protection Layer

Protection exists at 2 levels:

1️⃣ Timestamp filter (Producer)  
2️⃣ UNIQUE(event_id) constraint (Database)  

This creates idempotent ingestion.

---

## 🔁 Restart Safety

If:

- Kafka restarts
- Producer restarts
- Consumer restarts
- Server reboots

System remains consistent.

No duplicate.
No data corruption.
No offset loss.
