# 🚀 Quick Start Guide - Full Stack Network Anomaly Detection

## Complete Setup (5 Minutes)

### Step 1: Install Frontend Dependencies

```bash
cd frontend
npm install
```

### Step 2: Install API Dependencies

```bash
cd ..  # Back to project root
pip install -r api_requirements.txt
```

### Step 3: Generate Sample Attack Data

```bash
# Generate 100 packets with 30% anomalies
python anomaly_detection/main.py --mode detect --model random_forest \
  --interface lo --packet-count 100 --inject-rate 0.3 --synthetic-delay 0.01
```

Expected output:
```
Total Packets Processed: 100
Anomalies Detected: 30
Alerts Generated: 30
Anomaly Rate: 30.00%
```

### Step 4: Start API Server

Open a new terminal:

```bash
python api_server.py
```

You should see:
```
* Running on http://0.0.0.0:5000
```

Test it:
```bash
curl http://localhost:5000/health
# Should return: {"status":"healthy","timestamp":"..."}
```

### Step 5: Start Frontend

Open another terminal:

```bash
cd frontend
npm run dev
```

You should see:
```
- ready started server on 0.0.0.0:3000
- Local: http://localhost:3000
```

### Step 6: Open Dashboard

🎉 **Open your browser:** http://localhost:3000

You should see:
- ✅ 4 stat cards with packet counts
- ✅ 8 attack type cards (some showing detections)
- ✅ Timeline chart with activity
- ✅ Top threat sources list
- ✅ Recent detections table

---

## Running All Components Together

### Terminal 1: Detection System (Continuous)

```bash
# Keep generating traffic with anomalies
python anomaly_detection/main.py --mode detect --model random_forest \
  --interface lo --inject-rate 0.15 --synthetic-delay 0.1
```

This will continuously generate synthetic traffic with 15% anomalies.

### Terminal 2: API Server

```bash
python api_server.py
```

### Terminal 3: Frontend

```bash
cd frontend
npm run dev
```

### Terminal 4: Dashboard Viewer (Optional)

```bash
# Also run the original Dash dashboard for comparison
python anomaly_detection/main.py --mode dashboard
# Opens on http://127.0.0.1:8050
```

---

## What You Should See

### Next.js Dashboard (http://localhost:3000)

**Stats Cards:**
- Total Packets: Updates every 5 seconds
- Anomalies Detected: Shows red alerts
- Detection Rate: Percentage
- Recent Activity: Last hour count

**Attack Type Grid:**
Cards will light up and show counts for:
- 🔴 DoS/DDoS Attacks
- 🟠 Port Scanning
- 🟡 Brute Force
- 🌸 SQL Injection & XSS
- 🟣 Backdoor & Botnet
- 🔵 Data Exfiltration
- 🟢 Man-in-the-Middle
- 🔷 Zero-Day

**Timeline Chart:**
- Blue line: Total packets
- Red line: Anomalies
- Green line: Normal traffic

**Recent Detections Table:**
- Source/Dest IPs
- Protocol (TCP/UDP/ICMP)
- Anomaly score with progress bar
- Severity badges (HIGH/MEDIUM/LOW)

---

## Verification Commands

```bash
# Check database has data
sqlite3 data/detections.db "SELECT COUNT(*) FROM detections;"

# Check API is responding
curl http://localhost:5000/api/detections/stats | jq

# Check recent anomalies
curl http://localhost:5000/api/detections/by-type | jq '.counts'

# Check top sources
curl http://localhost:5000/api/detections/top-sources | jq
```

---

## Troubleshooting

### Problem: "No data showing on dashboard"

**Solution:**
```bash
# Run detection to populate data
python anomaly_detection/main.py --mode detect --model random_forest \
  --packet-count 50 --inject-rate 0.3
```

### Problem: "API connection refused"

**Solution:**
```bash
# Ensure API server is running
python api_server.py

# Test API
curl http://localhost:5000/health
```

### Problem: "npm install fails"

**Solution:**
```bash
cd frontend
rm -rf node_modules package-lock.json
npm cache clean --force
npm install
```

### Problem: "Port 3000 already in use"

**Solution:**
```bash
# Use different port
cd frontend
PORT=3001 npm run dev
# Then open http://localhost:3001
```

---

## Production Deployment

### Build Frontend

```bash
cd frontend
npm run build
npm start  # Production server on port 3000
```

### Run API in Production

```bash
# Use gunicorn for production
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 api_server:app
```

### With Docker (Optional)

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "5000:5000"
    volumes:
      - ./data:/app/data
    command: python api_server.py

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    depends_on:
      - api
    environment:
      - NEXT_PUBLIC_API_URL=http://api:5000
```

Run:
```bash
docker-compose up
```

---

## Demo Mode

Want impressive demo with lots of attacks?

```bash
# Generate 500 packets with 40% anomalies in 50 seconds
python anomaly_detection/main.py --mode detect --model random_forest \
  --packet-count 500 --inject-rate 0.4 --synthetic-delay 0.1
```

Then refresh dashboard to see:
- Attack type cards lighting up
- Timeline showing spike
- Recent detections flooding in
- Top sources populated

---

## Architecture Overview

```
┌─────────────────┐
│   Next.js UI    │  http://localhost:3000
│  (React/TS)     │
└────────┬────────┘
         │
         │ REST API
         ▼
┌─────────────────┐
│  Flask API      │  http://localhost:5000
│  (Python)       │
└────────┬────────┘
         │
         │ SQLite Queries
         ▼
┌─────────────────┐
│ detections.db   │  data/detections.db
│  (SQLite)       │
└────────┬────────┘
         ▲
         │ Writes
         │
┌─────────────────┐
│ Detection       │  Python ML System
│   System        │
└─────────────────┘
```

---

## Next Steps

1. **Customize Attack Classification**
   - Edit `api_server.py` → `classify_attack_type()` function
   - Add more sophisticated pattern matching

2. **Add Authentication**
   - Implement JWT tokens in API
   - Add login page to Next.js frontend

3. **Real Network Capture**
   - Run with sudo for real packet capture
   - Configure proper network interface (eth0, wlan0)

4. **Alerting**
   - Integrate email/SMS notifications
   - Connect to PagerDuty, Slack, etc.

5. **Scale Up**
   - Replace SQLite with PostgreSQL
   - Add Redis for caching
   - Deploy to Kubernetes

---

## Support

**Check Logs:**
```bash
# Application logs
tail -f logs/anomaly_detection.log

# API logs (in terminal running api_server.py)

# Frontend logs (browser console)
```

**Database Inspection:**
```bash
sqlite3 data/detections.db

# Useful queries
.tables
SELECT * FROM detections LIMIT 5;
SELECT COUNT(*) FROM detections WHERE is_anomaly = 1;
```

---

🎯 **You're all set! Enjoy your real-time network anomaly detection dashboard!**
