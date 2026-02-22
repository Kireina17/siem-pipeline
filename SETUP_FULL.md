# 🚀 Full Deployment Guide

This document describes complete deployment from clean Ubuntu server.

---

## 1️⃣ Install Dependencies

```bash
sudo apt update
sudo apt install -y python3 python3-venv wget git redis-server postgresql
```

---

## 2️⃣ Install Kafka (KRaft)

Download Kafka 3.8.0:

```bash
wget https://downloads.apache.org/kafka/3.8.0/kafka_2.13-3.8.0.tgz
tar -xzf kafka_2.13-3.8.0.tgz
mv kafka_2.13-3.8.0 kafka
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

## 3️⃣ Setup PostgreSQL

```sql
CREATE DATABASE siem;
CREATE USER siemuser WITH PASSWORD 'StrongPassword123';
GRANT ALL PRIVILEGES ON DATABASE siem TO siemuser;
```

Create alerts table:

```sql
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

---

## 4️⃣ Setup Python

```bash
python3 -m venv /home/dahfa/siem-env
source /home/dahfa/siem-env/bin/activate
pip install kafka-python psycopg2-binary redis requests
```

---

## 5️⃣ Enable Services

```bash
sudo systemctl enable kafka
sudo systemctl enable wazuh-producer
sudo systemctl enable backend-consumer
```

---

System ready.
