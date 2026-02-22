# 🚀 SIEM Pipeline

Custom lightweight SIEM pipeline integrating:

- Apache Kafka (KRaft mode)
- Wazuh Indexer
- Python Producer (Wazuh → Kafka)
- Python Backend Consumer (Kafka → Backend)

---

# 🎯 Purpose

This project streams Wazuh alerts into Kafka and processes them using a custom backend consumer.

It ensures:

- Real-time alert streaming
- Timestamp-based offset logic
- No duplicate log ingestion
- Lightweight architecture (no heavy SIEM stack)

---

# 🏗 Architecture

Wazuh Indexer  
⬇  
Python Producer (polling + timestamp offset)  
⬇  
Kafka Topic (`wazuh-alerts`)  
⬇  
Python Backend Consumer  

---

# ⚡ Quick Start (Minimal Setup)

```bash
sudo apt update
sudo apt install -y python3 python3-venv git wget curl
git clone https://github.com/Kireina17/siem-pipeline.git
cd siem-pipeline
python3 -m venv siem-env
source siem-env/bin/activate
pip install -r requirements.txt
```

Then:

1. Install Kafka  
2. Configure `.env`  
3. Start Producer & Consumer  

---

# 📦 Requirements

- Ubuntu 22.04 / 24.04
- Python 3.10+
- Git
- Internet access
- Wazuh already installed

---

# 🧱 1️⃣ Install Kafka (KRaft Mode)

Download Kafka:

```bash
wget https://downloads.apache.org/kafka/3.7.0/kafka_2.13-3.7.0.tgz
tar -xzf kafka_2.13-3.7.0.tgz
mv kafka_2.13-3.7.0 kafka
```

Generate Cluster ID:

```bash
KAFKA_CLUSTER_ID=$(kafka/bin/kafka-storage.sh random-uuid)
kafka/bin/kafka-storage.sh format -t $KAFKA_CLUSTER_ID -c kafka/config/kraft/server.properties
```

Start Kafka (test mode):

```bash
kafka/bin/kafka-server-start.sh kafka/config/kraft/server.properties
```

Verify Kafka is running:

```bash
ss -tulnp | grep 9092
```

---

# 🔐 2️⃣ Configure Environment Variables

Create `.env` file:

```bash
nano .env
```

Add:

```
WAZUH_USER=admin
WAZUH_PASS=your_password_here
KAFKA_BROKER=localhost:9092
TOPIC=wazuh-alerts
```

Load variables:

```bash
export $(cat .env | xargs)
```

---

# 📡 3️⃣ Run Producer

```bash
source siem-env/bin/activate
python producer/wazuh_producer.py
```

The producer will:

- Poll Wazuh Indexer
- Filter using `@timestamp > last_timestamp`
- Send only new alerts
- Avoid re-reading old logs

---

# 📥 4️⃣ Run Backend Consumer

```bash
source siem-env/bin/activate
python consumer/backend_consumer.py
```

---

# ⚙️ 5️⃣ Production Mode (systemd)

Copy service files:

```bash
sudo cp systemd/*.service /etc/systemd/system/
sudo systemctl daemon-reload
```

Enable services:

```bash
sudo systemctl enable kafka
sudo systemctl enable wazuh-producer
sudo systemctl enable backend-consumer
```

Start services:

```bash
sudo systemctl start kafka
sudo systemctl start wazuh-producer
sudo systemctl start backend-consumer
```

Check logs:

```bash
journalctl -u wazuh-producer -f
journalctl -u backend-consumer -f
journalctl -u kafka -f
```

---

# 🧠 Offset Logic Explanation

The producer uses:

```
@timestamp > last_timestamp
```

This guarantees:

- No duplicate ingestion
- No re-reading historical data
- Safe across day/month/year changes
- Continuous operation (2026 → 2027 → etc.)

---

# 🛠 Restore On New Server

On a fresh machine:

```bash
sudo apt install python3 python3-venv git wget
git clone https://github.com/Kireina17/siem-pipeline.git
cd siem-pipeline
python3 -m venv siem-env
source siem-env/bin/activate
pip install -r requirements.txt
```

Then:

- Reinstall Kafka
- Configure `.env`
- Start services

System restored.

---

# 📁 Project Structure

```
producer/        → Wazuh → Kafka sender
consumer/        → Kafka message processor
kafka/config/    → Kafka configuration
systemd/         → Production service files
requirements.txt → Python dependencies
```

---

# 🔒 Security Notes

- Use GitHub Personal Access Token (not password)
- Keep `.env` out of repository
- Never commit credentials
- Rotate tokens regularly

---

# 👑 Maintainer

**M Dahfa Ramadhan**  
Custom SIEM Pipeline – 2026
