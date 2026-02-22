# 🏗 SIEM Pipeline Architecture

## 🔥 Final Architecture

```
Wazuh Indexer (HTTPS + TLS CA)
        ↓
wazuh_producer.py (systemd service)
        ↓
Kafka (Topic: wazuh-alerts, 3 partitions)
        ↓
backend_consumer.py (systemd service)
        ↓
PostgreSQL (persistent storage)
        ↓
Redis (realtime cache layer)
```

---

## 🔄 Data Flow Explanation

### 1️⃣ Wazuh Indexer
- Stores security alerts
- Exposed via HTTPS
- TLS verified using root CA

### 2️⃣ Producer Layer
- Polls Wazuh every 5 seconds
- Filters using timestamp offset
- Sends only new alerts to Kafka

### 3️⃣ Kafka Layer
- 3 partitions
- Durable message queue
- Guarantees ordered delivery per partition

### 4️⃣ Backend Consumer
- Subscribes using group `dashboard-group`
- Inserts alerts into PostgreSQL
- Updates Redis cache
- Commits Kafka offset manually

### 5️⃣ PostgreSQL
- Persistent storage
- Duplicate safe via UNIQUE(event_id)

### 6️⃣ Redis
- Real-time counter
- Last 50 alerts cache
- Used for dashboard performance

---

## 🛡 Reliability Guarantees

✔ No duplicate alerts  
✔ Safe restart  
✔ Manual offset commit  
✔ TLS verification enabled  
✔ Service auto restart  
✔ Data persistence enabled  
