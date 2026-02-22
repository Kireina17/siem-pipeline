#  SIEM Pipeline #

Custom lightweight SIEM pipeline integrating:

- Apache Kafka (KRaft mode)
- Wazuh Indexer
- Python Producer (Wazuh → Kafka)
- Python Backend Consumer (Kafka → Backend)

---

# Architecture

Wazuh Indexer  
⬇  
Python Producer (polling with timestamp offset)  
⬇  
Kafka Topic (wazuh-alerts)  
⬇  
Python Backend Consumer  

---

# 📦 Requirements

- Ubuntu 22.04 / 24.04
- Python 3.10+
- Git
- Internet access
- Wazuh already installed

---

# 🧰 1️⃣ Install Dependencies

```bash
sudo apt update
sudo apt install -y python3 python3-venv git wget curl
```

---

# 🧱 2️⃣ Install Kafka (KRaft Mode)

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

Start Kafka manually (test mode):

```bash
kafka/bin/kafka-server-start.sh kafka/config/kraft/server.properties
```

Verify:

```bash
ss -tulnp | grep 9092
```

---

# 🐍 3️⃣ Setup Python Environment

Clone repository:

```bash
git clone https://github.com/Kireina17/siem-pipeline.git
cd siem-pipeline
```

Create virtual environment:

```bash
python3 -m venv siem-env
source siem-env/bin/activate
pip install -r requirements.txt
```

---

# 🔐 4️⃣ Configure Environment Variables

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

# 📡 5️⃣ Run Producer

```bash
source siem-env/bin/activate
python producer/wazuh_producer.py
```

It will:
- Poll Wazuh Indexer
- Use timestamp offset logic
- Send new alerts only
- Avoid re-reading old logs

---

# 📥 6️⃣ Run Backend Consumer

```bash
source siem-env/bin/activate
python consumer/backend_consumer.py
```

---

# ⚙️ 7️⃣ Production Mode (systemd)

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

Producer uses:

```
@timestamp > last_timestamp
```

This ensures:
- No duplicate logs
- No re-reading old data
- Safe across month/year change
- Works continuously (2026 → 2027 → etc.)

---

# 🛠 Restore On New Server

On new machine:

```bash
sudo apt install python3 python3-venv git wget
git clone https://github.com/Kireina17/siem-pipeline.git
cd siem-pipeline
python3 -m venv siem-env
source siem-env/bin/activate
pip install -r requirements.txt
```

Reinstall Kafka  
Set `.env`  
Start services  

Done.

---

# 🔥 Security Notes

- Use GitHub Personal Access Token (not password)
- Keep `.env` out of repository
- Never commit credentials
- Rotate tokens regularly

---

# 👑 Maintainer

M Dahfa Ramadhan  
SIEM Custom Pipeline – 2026  

---
