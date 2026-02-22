# 🚀 SIEM Pipeline

Production-ready lightweight SIEM ingestion pipeline.

Integrates:

- Wazuh Indexer (TLS secured)
- Apache Kafka (KRaft mode, 3 partitions)
- Python Producer (timestamp-based filtering)
- Python Backend Consumer (manual offset commit)
- PostgreSQL (persistent storage)
- Redis (real-time cache layer)

---

# 🎯 Purpose

This project streams Wazuh alerts into Kafka and processes them into a persistent database with real-time cache support.

It ensures:

- Real-time alert streaming
- Duplicate-safe ingestion
- Manual offset control
- Restart-safe architecture
- Persistent storage
- Cache layer for dashboards

---

# 🏗 Architecture

```
Wazuh Indexer (HTTPS + TLS CA)
        ↓
wazuh_producer.py (systemd service)
        ↓
Kafka (topic: wazuh-alerts, 3 partitions)
        ↓
backend_consumer.py (systemd service)
        ↓
PostgreSQL (persistent storage)
        ↓
Redis (realtime cache layer)
```

---

# 🛡 Reliability & Safety

This pipeline guarantees:

- TLS verification (no insecure requests)
- Timestamp-based producer filtering
- Manual Kafka offset commit
- PostgreSQL `UNIQUE(event_id)` protection
- Safe restart of all services
- No duplicate ingestion
- No data loss after crash
- Redis real-time metrics support

Designed for stable long-running production environments.

---

# 📦 Requirements

- Ubuntu 22.04 / 24.04
- Python 3.10+
- Apache Kafka (KRaft mode)
- PostgreSQL
- Redis
- Wazuh already installed

---

# ⚡ Quick Setup

## 1️⃣ Install Dependencies

```bash
sudo apt update
sudo apt install -y python3 python3-venv wget git redis-server postgresql
```

---

# 🧱 Kafka Setup (KRaft Mode)

Download Kafka 3.8.0:

```bash
wget https://downloads.apache.org/kafka/3.8.0/kafka_2.13-3.8.0.tgz
tar -xzf kafka_2.13-3.8.0.tgz
mv kafka_2.13-3.8.0 kafka
cd kafka
```

Generate cluster ID:

```bash
bin/kafka-storage.sh random-uuid
```

Format storage:

```bash
bin/kafka-storage.sh format -t <UUID> -c config/kraft/server.properties
```

Create topic:

```bash
bin/kafka-topics.sh --create \
--topic wazuh-alerts \
--bootstrap-server localhost:9092 \
--partitions 3 \
--replication-factor 1
```

---

# 🗄 PostgreSQL Setup

```bash
sudo systemctl enable postgresql
sudo systemctl start postgresql
sudo -u postgres psql
```

```sql
CREATE DATABASE siem;
CREATE USER siemuser WITH PASSWORD 'StrongPassword123';
GRANT ALL PRIVILEGES ON DATABASE siem TO siemuser;

\c siem

CREATE TABLE alerts (
    id SERIAL PRIMARY KEY,
    event_id TEXT UNIQUE,
    timestamp TIMESTAMP,
    agent_name TEXT,
    rule_level INT,
    rule_description TEXT,
    full_log TEXT
);
```

Exit with:

```sql
\q
```

---

# 🔴 Redis Setup

```bash
sudo systemctl enable redis-server
sudo systemctl start redis-server
```

Verify:

```bash
redis-cli ping
```

Expected output:

```
PONG
```

Redis is used for:

- Realtime alert counter
- Last 50 alerts cache
- Fast dashboard metrics

---

# 🐍 Python Environment Setup

```bash
git clone https://github.com/Kireina17/siem-pipeline.git
cd siem-pipeline

python3 -m venv siem-env
source siem-env/bin/activate
pip install -r requirements.txt
```

---

# 🔐 Environment Configuration

Create environment file:

```
/etc/wazuh-producer.env
```

Example:

```
WAZUH_USER=admin
WAZUH_PASS=your_password_here
```

---

# 🔐 Wazuh TLS Certificate Configuration

The producer connects to Wazuh Indexer using HTTPS with TLS verification.

Default certificate path (Wazuh 4.x):

```
/etc/wazuh-indexer/certs/root-ca.pem
```

Inside:

```
producer/wazuh_producer.py
```

Ensure this line matches your environment:

```python
WAZUH_CA_CERT = "/etc/wazuh-indexer/certs/root-ca.pem"
```

If your certificate path differs, update it accordingly.

To locate the CA certificate:

```bash
sudo find /etc -name "*root-ca*.pem"
```

⚠ Never use `verify=False`. Always validate TLS certificates in production.

If misconfigured, you may see:

```
SSL: CERTIFICATE_VERIFY_FAILED
```

---

# 📡 Run Producer

```bash
source siem-env/bin/activate
python producer/wazuh_producer.py
```

Producer:

- Polls Wazuh Indexer
- Filters using `@timestamp > last_timestamp`
- Sends only new alerts
- Prevents duplicate streaming

---

# 📥 Run Backend Consumer

```bash
source siem-env/bin/activate
python consumer/backend_consumer.py
```

Consumer:

- Subscribes to Kafka
- Inserts into PostgreSQL
- Uses `ON CONFLICT DO NOTHING`
- Updates Redis cache
- Commits Kafka offset manually

---

# ⚙ Production Mode (systemd)

```bash
sudo cp systemd/*.service /etc/systemd/system/
sudo systemctl daemon-reload

sudo systemctl enable kafka
sudo systemctl enable wazuh-producer
sudo systemctl enable backend-consumer

sudo systemctl start kafka
sudo systemctl start wazuh-producer
sudo systemctl start backend-consumer
```

---

# 🔍 Verification

Check services:

```bash
systemctl status kafka wazuh-producer backend-consumer
```

Check Kafka lag:

```bash
bin/kafka-consumer-groups.sh \
--bootstrap-server localhost:9092 \
--describe \
--group dashboard-group
```

Lag should be:

```
LAG = 0
```

Check Redis:

```bash
redis-cli GET total_alerts
```

Check PostgreSQL:

```sql
SELECT count(*) FROM alerts;
```

---

# 📁 Project Structure

```
producer/          → Wazuh → Kafka
consumer/          → Kafka → PostgreSQL + Redis
kafka/config/      → Kafka configuration
systemd/           → Production service files
requirements.txt   → Python dependencies
```

---

# 🔒 Security Notes

- Never commit passwords
- Keep `.env` out of repository
- Use GitHub Personal Access Token
- Rotate credentials periodically

---

# 👑 Maintainer

M Dahfa Ramadhan  
Mini Production-Ready SIEM Pipeline – 2026
